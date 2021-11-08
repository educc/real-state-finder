package app

case class  ApartmentItem(
                         district: String,
                         address: String,
                         priceByM2: BigDecimal,
                         url: String,
                         contact: Seq[String] = Seq.empty
                         )
