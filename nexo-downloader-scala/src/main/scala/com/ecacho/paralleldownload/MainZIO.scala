package com.ecacho.paralleldownload

import com.ecacho.paralleldownload.client.{NexoClient, Slug}
import zio.{Task, ZIO, ZIOAppDefault}

object MainZIO extends ZIOAppDefault {

  val DOWNLOAD_DIR = "nexo_cache"
  val downloadProjectLinks: Task[List[String]] =
    ZIO.fromFuture(implicit ec => (new NexoClient()).findProjectLinks())

  def create_download_dir_if_not_exists(): Task[Unit] =
    ZIO.attemptUnsafe { _ =>
      val dir = new java.io.File(DOWNLOAD_DIR)
      if (!dir.exists()) {
        dir.mkdir()
      }
    }

  def saveFile(name: String, html: String): Task[Unit] =
    ZIO.attemptUnsafe { _ =>
      val slug = Slug(name)
      val path = s"$DOWNLOAD_DIR/$slug.html"
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
      _ <- create_download_dir_if_not_exists()
      links <- downloadProjectLinks
      _ <- ZIO.foreachPar(links)(downloadAndSaveLink).withParallelism(8)
    } yield ()
}
