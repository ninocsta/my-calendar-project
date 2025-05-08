from rest_framework import serializers
from .models import Profissional, Servico, Agendamento, Cliente

class ProfissionalSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='nome')

    class Meta:
        model = Profissional
        fields = ['id', 'name']

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'nome', 'duracao_padrao', 'valor_padrao']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'telefone']

class AgendamentoSerializer(serializers.ModelSerializer):
    resourceId = serializers.PrimaryKeyRelatedField(queryset=Profissional.objects.all(), source='profissional', allow_null=False)
    startDate = serializers.DateTimeField(source='data_hora_inicio', format='%Y-%m-%dT%H:%M:%S%z', required=False)
    endDate = serializers.DateTimeField(source='data_hora_fim', format='%Y-%m-%dT%H:%M:%S%z', required=False)
    servico_id = serializers.PrimaryKeyRelatedField(queryset=Servico.objects.all(), source='servico', allow_null=False)
    cliente_id = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), source='cliente', allow_null=False)
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        # Concatenar nome do profissional e do serviço        
        servico_nome = obj.servico.nome if obj.servico else 'Desconhecido'
        cliente_nome = obj.cliente.nome if obj.cliente else 'Desconhecido'
        return f"{servico_nome} \r {cliente_nome}"

    class Meta:
        model = Agendamento
        fields = ['id', 'resourceId', 'startDate', 'endDate', 'name', 'valor_cobrado', 'servico_id', 'cliente_id']


class CalendarLoadSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    resources = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    def get_resources(self, obj):
        return {'rows': ProfissionalSerializer(obj['resources'], many=True).data}

    def get_events(self, obj):        
        return {'rows': AgendamentoSerializer(obj['events'], many=True).data}