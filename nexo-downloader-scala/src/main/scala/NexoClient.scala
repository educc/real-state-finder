import com.typesafe.scalalogging.Logger
import io.circe.*
import io.circe.parser.*
import okhttp3.OkHttpClient
import sttp.client3.okhttp.OkHttpFutureBackend
import sttp.client3.okhttp.quick.*

import scala.concurrent.{ExecutionContext, Future}

object NexoClient {

  private val logger = Logger(getClass.getSimpleName)
  private val okHttpClient: OkHttpClient =
    OkHttpClient
      .Builder()
      .callTimeout(java.time.Duration.ofSeconds(10))
      .build()
  private val backend = OkHttpFutureBackend.usingClient(okHttpClient)
  private val defaultUrl =
    "https://nexoinmobiliario.pe/departamentos/departamentos-lima"
  private val projectUrlPrefix =
    "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-"

  def get(url: String)(implicit
      ec: ExecutionContext
  ): Future[String] = {
    logger.info(s"Fetching $url")
    quickRequest
      .get(uri"$url")
      .send(backend)
      .map(_.body)
  }

  def findProjectLinks()(implicit
      ec: ExecutionContext
  ): Future[List[String]] = {
    logger.info(s"Fetching project links from $defaultUrl")
    fetchJsonString(defaultUrl)
      .map { it =>
        parse(it).toOption
          .map(arr => arr \\ "slug")
          .getOrElse(List.empty)
      }
      .map(it =>
        it
          .map(_.asString.getOrElse(""))
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
