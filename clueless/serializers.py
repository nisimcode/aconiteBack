from rest_framework import serializers

from .models import Cluster


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ["answer", "clues"]
        depth = 3
