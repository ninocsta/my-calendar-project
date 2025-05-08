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
    name = serializers.CharField(source='servico.nome', read_only=True)
    servico_id = serializers.PrimaryKeyRelatedField(queryset=Servico.objects.all(), source='servico', allow_null=False)
    cliente_id = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), source='cliente', allow_null=False)

    class Meta:
        model = Agendamento
        fields = ['id', 'resourceId', 'startDate', 'endDate', 'name', 'valor_cobrado', 'servico_id', 'cliente_id']

    def validate(self, data):
        print('Validando dados:', data)  # Para debug
        if 'data_hora_inicio' in data and 'data_hora_fim' in data:
            if data['data_hora_inicio'] >= data['data_hora_fim']:
                raise serializers.ValidationError("A data de fim deve ser posterior à data de início.")
            agendamentos = Agendamento.objects.filter(
                profissional=data.get('profissional', self.instance.profissional if self.instance else None),
                data_hora_inicio__lt=data['data_hora_fim'],
                data_hora_fim__gt=data['data_hora_inicio']
            )
            if self.instance:
                agendamentos = agendamentos.exclude(id=self.instance.id)
            if agendamentos.exists():
                raise serializers.ValidationError("Conflito de horário com outro agendamento.")
        return data

class CalendarLoadSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    resources = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    def get_resources(self, obj):
        return {'rows': ProfissionalSerializer(obj['resources'], many=True).data}

    def get_events(self, obj):
        return {'rows': AgendamentoSerializer(obj['events'], many=True).data}