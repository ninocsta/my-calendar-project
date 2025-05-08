from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Profissional, Servico, Agendamento, Cliente
from .serializers import CalendarLoadSerializer, AgendamentoSerializer, ProfissionalSerializer, ServicoSerializer, ClienteSerializer

class CalendarLoadView(APIView):
    def get(self, request):
        profissionais = Profissional.objects.all()
        agendamentos = Agendamento.objects.all()
        servicos = Servico.objects.all()
        serializer = CalendarLoadSerializer({
            'success': True,
            'resources': profissionais,
            'events': agendamentos,
            'servico_id': servicos
        })
        return Response(serializer.data)

class CalendarSyncView(APIView):
    def post(self, request):
        data = request.data
        print('Dados recebidos no sync:', data)  # Para debug
        response = {
            'success': True,
            'events': {'rows': []},
            'assignments': {'rows': []}
        }

        # Processar eventos
        if 'events' in data:
            events = data['events']

            # Adição de eventos
            if 'added' in events:
                for event_data in events['added']:
                    print('Processando adição:', event_data)
                    serializer = AgendamentoSerializer(data=event_data)
                    if serializer.is_valid():
                        agendamento = serializer.save()
                        # Adicionar à resposta o $PhantomId e o id real
                        response['events']['rows'].append({
                            '$PhantomId': event_data.get('$PhantomId'),
                            'id': agendamento.id
                        })
                    else:
                        print('Erro na adição:', serializer.errors)
                        return Response({
                            'success': False,
                            'errors': serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)

            # Atualização de eventos
            if 'updated' in events:
                for event_data in events['updated']:
                    print('Processando atualização:', event_data)
                    try:
                        agendamento = Agendamento.objects.get(id=event_data['id'])
                        serializer = AgendamentoSerializer(agendamento, data=event_data, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                            # Adicionar à resposta o id atualizado
                            response['events']['rows'].append({
                                'id': agendamento.id
                            })
                        else:
                            print('Erro na atualização:', serializer.errors)
                            return Response({
                                'success': False,
                                'errors': serializer.errors
                            }, status=status.HTTP_400_BAD_REQUEST)
                    except Agendamento.DoesNotExist:
                        print(f"Agendamento {event_data['id']} não encontrado")
                        return Response({
                            'success': False,
                            'error': f"Agendamento {event_data['id']} não encontrado"
                        }, status=status.HTTP_404_NOT_FOUND)

            # Remoção de eventos
            if 'removed' in events:
                for event_data in events['removed']:
                    print('Processando remoção:', event_data)
                    Agendamento.objects.filter(id=event_data['id']).delete()
                    # Adicionar à resposta o id removido
                    response['events']['rows'].append({
                        'id': event_data['id']
                    })

        # Processar assignments (associações de eventos a recursos)
        if 'assignments' in data:
            assignments = data['assignments']
            if 'added' in assignments:
                for assignment_data in assignments['added']:
                    print('Processando assignment:', assignment_data)
                    # No seu caso, assignments são redundantes, pois resourceId já está no evento
                    # Retornamos o $PhantomId e o resourceId para satisfazer o Bryntum
                    response['assignments']['rows'].append({
                        '$PhantomId': assignment_data.get('$PhantomId'),
                        'id': assignment_data.get('resourceId')
                    })

        print('Resposta enviada:', response)  # Para debug
        return Response(response)

class ProfissionalListView(APIView):
    def get(self, request):
        profissionais = Profissional.objects.all()
        serializer = ProfissionalSerializer(profissionais, many=True)
        return Response(serializer.data)

class ServicoListView(APIView):
    def get(self, request):
        servicos = Servico.objects.all()
        serializer = ServicoSerializer(servicos, many=True)
        return Response(serializer.data)

class ClienteListView(APIView):
    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)