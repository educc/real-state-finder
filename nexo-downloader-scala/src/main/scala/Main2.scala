import com.typesafe.scalalogging.Logger

import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration.*
import scala.concurrent.{Await, ExecutionContext, Future}

object Main2 extends App {

  val logger = Logger(getClass.getSimpleName)
  val outputDir = "output-html"

  def downloadLink(
      link: String
  )(implicit ec: ExecutionContext): Future[Any] = {
    logger.info(s"Starting download for link: $link")

    NexoClient
      .get(link) // Assuming NexoClient.get returns Future[Unit]
      .map(_ => logger.info(s"Downloaded and saved content from $link"))

  }

  val link =
    "https://nexoinmobiliario.pe/proyecto/venta-de-departamento-2361-paseo-de-la-arboleda-4"
  val futureDownload = downloadLink(link)

  // Use a reasonable timeout instead of Duration.Inf
  try {
    Await.result(futureDownload, 10.minutes)
  } catch {
    case e: Exception =>
      logger.error(
        "An error occurred while waiting for download to complete",
        e
      )
  }

  // Allow the application to exit naturally
  logger.info("Application has finished executing.")
}
