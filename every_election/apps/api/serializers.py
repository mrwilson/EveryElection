from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer, GeometrySerializerMethodField)

from elections.models import (
    Election, ElectionType, ElectionSubType, VotingSystem)
from organisations.models import (Organisation, OrganisationDivision,
                                  OrganisationDivisionSet)


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        lookup_field = 'official_identifier'
        fields = (
            'official_identifier',
            'organisation_type',
            'organisation_subtype',
            'official_name',
            'common_name',
            'gss',
            'slug',
            'territory_code',
            'election_name'
        )

class OrganisationGeoSerializer(GeoFeatureModelSerializer):

    geography_model = GeometrySerializerMethodField()

    def get_geography_model(self, obj):
        return obj.geography.geography.simplify(0.0009)

    class Meta:
        model = Organisation
        extra_kwargs = {
            'url': {
                'view_name': 'organisation-geo',
                'lookup_field': 'pk'
            }
        }

        geo_field = 'geography_model'

        fields = (
            'official_identifier',
            'organisation_type',
            'organisation_subtype',
            'official_name',
            'common_name',
            'gss',
            'slug',
            'territory_code',
            'election_name'
        )


class OrganisationDivisionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationDivisionSet
        fields = (
            'start_date',
            'end_date',
            'legislation_url',
            'consultation_url',
            'short_title',
            'mapit_generation_id',
            'notes',
        )


class OrganisationDivisionSerializer(serializers.ModelSerializer):
    divisionset = OrganisationDivisionSetSerializer()
    class Meta:
        model = OrganisationDivision
        fields = (
            'divisionset',
            'name',
            'official_identifier',
            'geography_curie',
            'slug',
            'division_type',
            'division_subtype',
            'division_election_sub_type',
            'seats_total',
            'mapit_generation_low',
            'mapit_generation_high',
            'territory_code',
        )


class ElectionTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ElectionType
        fields = ('name', 'election_type')
        depth = 1


class ElectionSubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectionSubType
        fields = ('name', 'election_subtype')


class VotingSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VotingSystem
        fields = ('slug', 'name', 'uses_party_lists')


class ElectedRoleField(serializers.RelatedField):
    def to_representation(self, value):
        return value.elected_title


class ExplanationSerializer(serializers.RelatedField):
    def to_representation(self, value):
        return value.explanation


class ElectionSerializer(serializers.HyperlinkedModelSerializer):
    election_type = ElectionTypeSerializer()
    election_subtype = ElectionSubTypeSerializer()
    organisation = OrganisationSerializer()
    division = OrganisationDivisionSerializer()
    group = serializers.SlugRelatedField(
        slug_field='election_id',
        read_only=True
        )
    children = serializers.SlugRelatedField(
        slug_field='election_id',
        read_only=True,
        many=True
    )
    elected_role = ElectedRoleField(read_only=True)
    voting_system = serializers.SerializerMethodField()
    explanation = ExplanationSerializer(read_only=True)

    # Current
    current = serializers.SerializerMethodField()

    def get_current(self, obj):
        return obj.get_current

    def get_voting_system(self, obj):
        if obj.group_type == 'organisation' or not obj.group_type:
            return VotingSystemSerializer(obj.voting_system).data
        return None

    class Meta:
        model = Election
        fields = (
            'election_id',
            'tmp_election_id',
            'election_title',
            'poll_open_date',
            'election_type',
            'election_subtype',
            'organisation',
            'group',
            'group_type',
            'children',
            'elected_role',
            'division',
            'voting_system',
            'current',
            'explanation',
        )
        depth = 1

