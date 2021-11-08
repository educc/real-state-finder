package app

import app.impl.NexoInmobiliariaFinder

object Main {

  def toCsv(fn: () => Seq[ApartmentItem]): String = {
    def toLine(it: ApartmentItem): String = {
      Seq(it.district, it.address, it.priceByM2, it.contact, it.url)
      .map {
        case a: Seq[_] => a.mkString("-")
        case b => b.toString
      }.mkString(",")
    }

    "district, address,m2 price, phones, url \n" +
    fn.apply()
      .map(toLine)
      .mkString("\n")
  }

  def main(args: Array[String]) = {
    val fn = () => NexoInmobiliariaFinder.find
    println(toCsv(fn))
  }

}
