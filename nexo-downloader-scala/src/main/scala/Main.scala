import com.typesafe.scalalogging.Logger

import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, Future}
// global import ec
import scala.concurrent.ExecutionContext.Implicits.global

object Main extends App {

  val logger = Logger(getClass.getSimpleName)

  // Creating execution context with 8 threads
//  val ec: ExecutionContext =
//    ExecutionContext.fromExecutorService(
//      new ForkJoinPool(8)
//    )

  val outputDir = "output-html"

  def downloadLink(
      link: String
  )(implicit ec: ExecutionContext): Future[Unit] = {
    logger.info(s"Starting download for link: $link")

    NexoClient
      .get(link)
//      .map { it =>
//        logger.info(s"Downloaded and saved content from $link")
//        val slug = Slug(link)
//        val path = s"$outputDir/$slug.html"
//
//        ()
//      }
      .map(_ => ())

  }

//  val result = NexoClient.findProjectLinks()
//
//  val listOfLinks = Await.result(result, Duration.Inf)

//  val allFutures = listOfLinks.map(downloadLink)
//  val first = downloadLink(listOfLinks.head)
  val first = downloadLink(
    "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2361-paseo-de-la-arboleda-4"
  )

  Await.result(first, Duration.Inf)

  System.exit(0)
}
