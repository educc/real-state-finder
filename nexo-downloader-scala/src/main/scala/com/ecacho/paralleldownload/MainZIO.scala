package com.ecacho.paralleldownload

import com.ecacho.paralleldownload.client.{NexoClient, Slug}
import zio.{Task, ZIO, ZIOAppDefault}

object MainZIO extends ZIOAppDefault {

  val downloadProjectLinks: Task[List[String]] =
    ZIO.fromFuture(implicit ec => (new NexoClient()).findProjectLinks())

  def saveFile(name: String, html: String): Task[Unit] =
    ZIO.attemptUnsafe { _ =>
      val slug = Slug(name)
      val path = s"nexo_cache/$slug.html"
      println(s"Writing to file: $path")
      java.nio.file.Files.write(java.nio.file.Paths.get(path), html.getBytes)
      ()
    }

  val downloadAndSaveLink: String => Task[Unit] = link =>
    for {
      html <- ZIO.fromFuture(implicit ec => (new NexoClient()).get(link))
      _ <- saveFile(link, html)
    } yield ()

  def run = myAppLogic

  val myAppLogic =
    for {
      links <- downloadProjectLinks
      _ <- ZIO.foreachPar(links)(downloadAndSaveLink).withParallelism(8)
    } yield ()
}
