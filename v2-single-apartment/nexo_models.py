from dataclasses import dataclass, field


@dataclass
class ProjectInfo:
    area_max: str | None = None
    area_min: str | None = None
    bathroom_max: str | None = None
    bathroom_min: str | None = None
    builder_name: str | None = None
    builder_slug: str | None = None
    cantidad: str | None = None
    cintillo_principal: str | None = None
    coin: str | None = None
    coord_lat: str | None = None
    direccion: str | None = None
    distrito: str | None = None
    dpto_project: str | None = None
    finance_bank: str | None = None
    gallery: list[str] = field(default_factory=list)
    gallery_big: list[str] = field(default_factory=list)
    gallery_xm: list[str] = field(default_factory=list)
    image: str | None = None
    important_level: str | None = None
    is_featured: str | None = None
    keyword: str | None = None
    logo_empresa: str | None = None
    long: str | None = None
    min_price: str | None = None
    name: str | None = None
    parking_max: str | None = None
    parking_min: str | None = None
    project_cell_phone: str | None = None
    project_contact: str | None = None
    project_email: str | None = None
    project_id: str | None = None
    project_phase: str | None = None
    project_phone: str | None = None
    project_whatsapp: str | None = None
    provincia_project: str | None = None
    room_max: str | None = None
    room_min: str | None = None
    services: str | None = None
    slug: str | None = None
    socio_asei: str | None = None
    tiene_promo_fn: str | None = None
    tour_virtual: str | None = None
    type_project: str | None = None
    url: str | None = None
    url_video: str | None = None
    val_price1: str | None = None
    val_price2: str | None = None
    visibility_ferianexo: str | None = None
    visibility_in_feria_nexo: str | None = None
    visibility_semananexo: str | None = None

    def __post_init__(self):
        # Convert comma-separated strings to lists
        self.gallery = self.gallery.split(',') if self.gallery else []
        self.gallery_xm = self.gallery_xm.split(',') if self.gallery_xm else []
        self.gallery_big = self.gallery_big.split(
            ',') if self.gallery_big else []
