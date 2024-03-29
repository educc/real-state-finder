//> using scala "3"
//> using lib "com.github.scopt::scopt:4.1.0"
//> using lib "io.circe::circe-core:0.14.5"
//> using lib "io.circe::circe-generic:0.14.5"
//> using lib "io.circe::circe-parser:0.14.5"

import scopt.OParser

object Main {

  case class Config(
      url: String =
        "https://nexoinmobiliario.pe/busqueda/venta-de-departamentos-en-lima-lima-1501"
  )

  val argParser = {
    val builder = OParser.builder[Config]
    {
      import builder._
      OParser.sequence(
        programName("real-state-finder"),
        head("real-state-finder", "1.0"),
        opt[String]('u', "url or file")
          .action((x, c) => c.copy(url = x))
          .text("URL to search for apartments")
      )
    }
  }

  def main(args: Array[String]) = {
    OParser.parse(argParser, args, Config()) match {
      case Some(config) =>
        println(
          "distrito, direccion, precioM2, areaMin, areaMax, roomMin, roomMax, phase, contact, url"
        )
        val isUrl = config.url.startsWith("http")

        val data = if (isUrl) {
          NexoInmobiliariaFinder.findFromUrl(config.url)
        } else {
          NexoInmobiliariaFinder.findFromJson(config.url)
        }

        data
          .map(_.toCsv)
          .foreach(println)
      case _ =>
        println("Arguments needed to run the program")
    }
  }

}
