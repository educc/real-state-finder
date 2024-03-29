import io.circe.parser.parse
import java.nio.file.{Files, Paths}
import scala.io.Source
import java.nio.charset.StandardCharsets

object NexoInmobiliariaFinder {

  def findFromUrl(url: String): Seq[ApartmentItem] = {
    val jsonStr = findJsonFromUrl(url)
    parse(jsonStr)
      .flatMap(_.as[Seq[ApartmentItem]])
      .getOrElse(Seq.empty)
  }

  def findFromJson(filename: String): Seq[ApartmentItem] = {
    parse(Source.fromFile(filename).mkString)
      .flatMap(_.as[Seq[ApartmentItem]])
      .getOrElse(Seq.empty)
  }

  def findJsonFromUrl(url: String): String = {
    val html = download(url)
    val json = findJson(html)
    json
  }

  private def download(url: String): String = {
    Source.fromURL(url, StandardCharsets.UTF_8.toString).mkString
  }

  private def findJson(html: String): String = {
    val start = html.indexOf("search_data=[")
    val end = html.indexOf("];\n", start + 1)
    html.substring(start + 12, end + 1)
  }

  // private def readFile = Files.readString(Paths.get(source))

}
