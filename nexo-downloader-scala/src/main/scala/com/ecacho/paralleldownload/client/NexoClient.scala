package com.ecacho.paralleldownload.client

import com.typesafe.scalalogging.Logger
import sttp.client3.okhttp.OkHttpFutureBackend
import sttp.client3.{UriContext, quickRequest}
import upickle.default.read

import scala.concurrent.{ExecutionContext, Future}

class NexoClient()(implicit ec: ExecutionContext) {

  private val logger = Logger(getClass.getSimpleName)
  private val backend = OkHttpFutureBackend()
  private val defaultUrl =
    "https://nexoinmobiliario.pe/departamentos/departamentos-lima"
  private val projectUrlPrefix =
    "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-"

  def get(url: String): Future[String] = {
    quickRequest
      .get(uri"$url")
      .send(backend)
      .map {
        case response if response.code.isSuccess => response.body
        case response =>
          throw new Exception(s"Failed to fetch $url: ${response.code}")
      }
  }

  def findProjectLinks(): Future[List[String]] = {
    logger.info(s"Fetching project links from $defaultUrl")
    fetchJsonString(defaultUrl)
      .map { it =>
        read[List[ProjectItem]](it)
      }
      .map(it =>
        it
          .map(_.slug)
          .map(slug => s"$projectUrlPrefix$slug")
      )
  }

  private def fetchJsonString(
      url: String
  )(implicit ec: ExecutionContext): Future[String] = {
    quickRequest
      .get(uri"$url")
      .send(backend)
      .map(_.body)
      .map(findJsonContent)
  }

  private def findJsonContent(html: String): String = {
    html
      .lines()
      .map(_.trim)
      .filter(_.contains("search_data"))
      .map(it => {
        val start = it.indexOf("[")
        val end = it.lastIndexOf("]")
        it.substring(start, end + 1)
      })
      .findFirst()
      .orElse("[]")
  }
}
