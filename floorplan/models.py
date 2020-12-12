from django.db import models
from django.shortcuts import reverse
# Create your models here.

class FloorPlan(models.Model):
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=150, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_download = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(verbose_name = 'image', upload_to = 'images/')
    json_path = models.FileField(verbose_name = 'graph', upload_to = 'jsons/')

    def get_absolute_url(self):
        return reverse('plan_detail_url', kwargs = {'slug': self.slug})

    def __str__(self):
        return self.title

    def get_image(self):
        return self.image.name

    def get_graph(self):
        return self.json_path

    def set_json(self, FILE):
        self.json_path = FILE