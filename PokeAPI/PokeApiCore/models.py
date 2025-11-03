from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Carta(models.Model):
    id = models.AutoField(primary_key=True)
    id_api = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    type = models.CharField(max_length=255, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    rarity = models.CharField(max_length=255, null=True, blank=True)
    number = models.CharField(max_length=255, null=True, blank=True)
    set_id = models.CharField(max_length=255, null=True, blank=True)
    set_name = models.CharField(max_length=255, null=True, blank=True)
    stage = models.CharField(max_length=255, null=True, blank=True)
    especial_type = models.CharField(max_length=255, null=True, blank=True)
    trainer = models.CharField(max_length=255, null=True, blank=True)
    edition = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.id_api})"


class UsuarioCarta(models.Model):
    id = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, to_field='nombre'
    )
    carta = models.ForeignKey(
        Carta, on_delete=models.CASCADE, to_field='id_api'
    )

    class Meta:
        unique_together = ('usuario', 'carta')

    def __str__(self):
        return f"{self.usuario} tiene {self.carta}"
