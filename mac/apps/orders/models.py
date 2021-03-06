from collections import namedtuple

from django.db import models
from django.contrib.auth import get_user_model


Product = namedtuple('Product', [
    'id',
    'name_ru',
    'description_template',
    'description',
    'image_url',
    'components'
])

PRODUCTS = [
    Product(
        id="shield",
        name_ru="Защитный Экран",
        description_template="sheet",
        description="Предназначен для защиты лица от жидких и твердых веществ. Она состоит из оправы, белой опоры и щитка в виде прозрачной пленки.",
        image_url="https://cleanroomshop.ru/upload/iblock/b54/schitok_1.jpg",
        components='Пластик'
    ),
    Product(
        id="valve",
        name_ru="Клапан",
        description_template="valve",
        description="Клапаны применяются в аппаратах ИВЛ совместно с аэрозольными масками для дозированной оксигенотерапии и обеспечивают пониженные концентрации подаваемого кислорода.",
        image_url="https://lh3.googleusercontent.com/proxy/Dv-Eg0jxAN2H7lnNQ3CIZ60xRKgjC7FSlw4PPmot8-K37riJ_9Z7YqNuzrT7mBssMZRXjl3X9midUi_AHIB2IM_FCCgyzQ",
        components='Пластик',
    ),
    Product(
        id="adapter_for_PMM88",
        name_ru="Деталь переходник с фильтра для аппарата ИВЛ на маску ППМ-88.",
        description_template="valve",
        description="Деталь переходник с фильтра для аппарата ИВЛ на маску ППМ-88.",
        image_url="https://cdn1.imggmi.com/uploads/2020/4/10/7ef00e17dab28d4bd0d56348889dc381-full.png",
        components='PetG со 100% заполнением!',
    ),
    Product(
        id="adapter_for_SUBEA",
        name_ru="Деталь переходник с фильтра для аппарата ИВЛ на маску для снорклинга компании SUBEA.",
        description_template="valve",
        description="Деталь переходник с фильтра для аппарата ИВЛ на маску для снорклинга компании SUBEA.",
        image_url="https://cdn1.imggmi.com/uploads/2020/4/10/552506c6bb57cbc5300324781706c900-full.png",
        components='PetG со 100% заполнением!',
    )
]


class Ticket(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    TYPE_PRODUCE = "produce"
    TYPE_REQUEST = "request"

    TYPE_CHOICES = [
        (TYPE_PRODUCE, "Произвоственный тикет"),
        (TYPE_REQUEST, "Запрос изделий"),
    ]

    type = models.TextField(
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0],
        verbose_name="Тип тикета",
    )

    LOGISTICS_CHOICES = [
        ("can_deliver", "Могу доставить"),
        ("need_delivery", "Нужен курьер"),
    ]

    logistics = models.TextField(
        choices=LOGISTICS_CHOICES,
        default=LOGISTICS_CHOICES[0],
        verbose_name="Логистика",
    )

    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='tickets')
    product = models.TextField(
        choices=[(product.id, product.name_ru) for product in PRODUCTS],
        default=PRODUCTS[0].id,
        verbose_name="Изделие"
    )

    amount = models.IntegerField(
        default=10,
        verbose_name="Количество"
    )

    comment = models.TextField(
        verbose_name="Комментарий"
    )

    def update_cached_properties(self):
        """
        We cache all those properties in order to filter using them.
        """
        self.city_cached = self.city

        self.is_production_ready_cached = self.is_production_ready
        self.is_production_delivered_cached = self.is_production_delivered

        self.save(update_fields=[
            'city_cached',
            'is_production_ready_cached',
            'is_production_delivered_cached',
        ])

    @property
    def address(self):
        return self.author.address

    city_cached = models.TextField(
        choices=get_user_model().CITIES,
        default=get_user_model().CITIES[0],
        verbose_name="Город",
    )

    @property
    def city(self):
        return self.author.city

    is_production_ready_cached = models.BooleanField(
        default=False,
        verbose_name="Производство завершено"
    )

    is_production_delivered_cached = models.BooleanField(
        default=False,
        verbose_name="Изделия доставлены получателю"
    )

    @property
    def is_production_ready(self):
        return self.updates.filter(type=TicketUpdate.TYPE_IS_PRODUCED).count() > 0

    @property
    def is_production_delivered(self):
        return self.updates.filter(type=TicketUpdate.TYPE_IS_DELIVERED).count() > 0


class TicketUpdate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='ticket_updates')
    target_ticket = models.ForeignKey(Ticket, on_delete=models.PROTECT, related_name='updates')

    TYPE_COMMENT = 'comment'
    TYPE_IS_PRODUCED = "is_produced"
    TYPE_IS_DELIVERED = "is_delivered"

    TYPE = [
        (TYPE_COMMENT, "Комментарий"),
        (TYPE_IS_PRODUCED, "Партия произведена"),
        (TYPE_IS_DELIVERED, "Партия доставлена"),
    ]

    type = models.TextField(
        choices=TYPE,
        default=TYPE[0][0],
        verbose_name="Тип обновления",
    )

    comment = models.TextField(
        verbose_name="Комментарий"
    )
