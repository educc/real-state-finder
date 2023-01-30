//> using lib "io.circe::circe-core:0.14.1"
//> using lib "io.circe::circe-generic:0.14.1"
//> using lib "io.circe::circe-parser:0.14.1"

object Main {

  def toCsv(fn: () => Seq[ApartmentItem]): String = {
    def toLine(it: ApartmentItem): String = {
      Seq(it.district, it.address, it.priceByM2, it.areaMin, it.areaMax, it.contact, it.url)
      .map {
        case a: Seq[_] => a.mkString("-")
        case b => b.toString
      }.mkString(",")
    }

    "district, address,m2 price, area min, area max, phones, url \n" +
    fn.apply()
      .map(toLine)
      .mkString("\n")
  }

  def main(args: Array[String]) = {
    val fn = () => NexoInmobiliariaFinder.find
    println(toCsv(fn))
  }

}
