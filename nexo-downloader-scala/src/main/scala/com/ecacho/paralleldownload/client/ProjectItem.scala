package com.ecacho.paralleldownload.client

import upickle.default.{ReadWriter, macroRW}

case class ProjectItem(
    slug: String
)

object ProjectItem {
  implicit val rw: ReadWriter[ProjectItem] = macroRW
}
