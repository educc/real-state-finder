import com.typesafe.scalalogging.Logger

import java.nio.file.Files
import java.util.concurrent.ForkJoinPool
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, Future}
// global import ec
//import scala.concurrent.ExecutionContext.Implicits.global

object Main extends App {

  val logger = Logger(getClass.getSimpleName)

  // Creating execution context with 8 threads
  implicit val ec: ExecutionContext =
    ExecutionContext.fromExecutorService(
      new ForkJoinPool(8)
    )

  val outputDir = "nexo_cache"
  val nexoClient = new NexoClient()

  def downloadLink(link: String) = {
    nexoClient
      .get(link)
      .map { html =>
        val slug = Slug(link)
        val path = s"$outputDir/$slug.html"
        logger.info(s"Writing to file: $path")
        Files.write(java.nio.file.Paths.get(path), html.getBytes)
      }
      .recover { case e: Exception =>
        logger.error(s"Failed to download $link", e)
      }

  }

  val result = nexoClient.findProjectLinks()
  val listOfLinks = Await.result(result, Duration.Inf)

  val allFutures = Future.sequence(
    listOfLinks.map(downloadLink)
  )

  Await.result(allFutures, Duration("10 minutes"))

  System.exit(0)
}
