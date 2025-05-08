import { Calendar, Toast, EventModel, Store } from '@bryntum/calendar';
import './style.css'
// Custom EventModel subclass for Agendamento
class Agendamento extends EventModel {
    static get fields() {
        return [
            { name: 'servico_id', type: 'number' },
            { name: 'cliente_id', type: 'number' },
            { name: 'valor_cobrado', type: 'number' }
        ];
    }
}

// Function to fetch data from DRF and format for combo fields
async function fetchComboData(endpoint) {
    try {
        const response = await fetch(`http://localhost:8000/api/${endpoint}/`);
        if (!response.ok) throw new Error(`Falha ao buscar ${endpoint}`);
        const data = await response.json();
        console.log(`Dados de ${endpoint} recebidos:`, data);
        return data.map(item => ({
            id: item.id,
            text: item.name || item.nome
        }));
    } catch (error) {
        console.error(`Erro ao buscar ${endpoint}:`, error);
        return [];
    }
}

// Definição das stores para os combos
const profissionaisStore = new Store({
    data: [],
    model: {
        fields: ['id', 'text']
    }
});

const servicosStore = new Store({
    data: [],
    model: {
        fields: ['id', 'text']
    }
});

const clientesStore = new Store({
    data: [],
    model: {
        fields: ['id', 'text']
    }
});

// Fetch combo data and initialize calendar
Promise.all([
    fetchComboData('profissionais'),
    fetchComboData('servicos'),
    fetchComboData('clientes')
]).then(([profissionais, servicos, clientes]) => {
    // Preencher as stores com os dados
    profissionaisStore.data = profissionais;
    servicosStore.data = servicos;
    clientesStore.data = clientes;
    console.log('Stores preenchidas:', {
        profissionais: profissionaisStore.data,
        servicos: servicosStore.data,
        clientes: clientesStore.data
    });

    const calendar = new Calendar({
        appendTo: 'app',
        mode: 'week',
        timeZone: 'America/Sao_Paulo',
        date: new Date(),
        eventModelClass: Agendamento,
        timeZone: 'America/Sao_Paulo',        
        crudManager: {
            autoLoad: true,
            autoSync: true,
            transport: {
                load: {
                    url: '/api/calendar/load/',
                    method: 'GET',
                    paramName: 'data',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    params: {
                        requestType: 'load'
                    },
                    credentials: 'include',
                    cache: 'no-cache'
                },
                sync: {
                    url: '/api/calendar/sync/',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    params: {
                        requestType: 'sync'
                    },
                    credentials: 'include'
                }
            },
            listeners: {
                beforeLoad({ source, pack }) {
                    console.log('Before load:', pack);
                    pack.stores = ['resources', 'events'];
                },
                load({ response }) {
                    console.log('Dados do calendário carregados:', response);
                },
                loadFail({ response }) {
                    console.error('Falha ao carregar dados do calendário:', response);
                },
                sync({ response }) {
                    console.log('Dados sincronizados:', response);
                },
                syncFail({ response }) {
                    console.error('Falha na sincronização:', response);
                },
                beforeSync({ source, pack }) {
                    console.log('Enviando sync:', pack);
                    // Ensure custom fields are included in sync payload
                    if (pack.events && pack.events.added) {
                        pack.events.added.forEach(event => {
                            event.allDay = false;
                            if (event.servico_id) event.servico_id = Number(event.servico_id);
                            if (event.cliente_id) event.cliente_id = Number(event.cliente_id);
                            if (event.valor_cobrado) event.valor_cobrado = Number(event.valor_cobrado);
                        });
                    }
                    if (pack.events && pack.events.updated) {
                        pack.events.updated.forEach(event => {
                            event.allDay = false;
                            if (event.servico_id) event.servico_id = Number(event.servico_id);
                            if (event.cliente_id) event.cliente_id = Number(event.cliente_id);
                            if (event.valor_cobrado) event.valor_cobrado = Number(event.valor_cobrado);
                        });
                    }
                },
                hasChanges() {
                    Toast.show({
                        html: JSON.stringify(calendar.crudManager.changes, true, 4).replaceAll('\n', '<br>').replaceAll(/\s/g, '\xa0'),
                        timeout: 5000
                    });
                }
            }
        },
        sidebar: {
            items: {
                resourceFilter: {
                    title: 'Profissionais',
                    selected: profissionais.map(p => p.id)

                },                
            }
        },
        modeDefaults: {
            view: {                
                strips: {
                    resourceInfo: {
                        type: 'widget',
                        dock: 'header',
                        cls: 'b-resource-location',
                        
                    }
                }
            }
        },
        modes: {
            day: null,
            week: null,
            month: null,
            year: null,
            agenda: null,
            dayResources: {
                type: 'resource',
                title: 'Dia',
                resourceWidth: '30em',  
                view: {
                    type: 'dayview',
                },            
                meta: resource => resource.text
            },
            weekResources: {
                type: 'resource',
                title: 'Semana',
                resourceWidth: '30em',
                hideNonWorkingDays: true,
                view: {
                    dayStartTime: 8
                },
                meta: resource => resource.text
            },
            monthResources: {
                type: 'resource',
                title: 'Mês',
                resourceWidth: '30em',
                hideNonWorkingDays: true,
                view: {
                    type: 'monthview'
                },
                meta: resource => resource.text
            }
        },
        tbar: {
            items: {
                label: {
                    type: 'label',
                    text: 'Largura do recurso',
                    weight: 630
                },
                viewWidth: {
                    type: 'slider',
                    weight: 640,
                    min: 12,
                    max: 100,
                    value: 30,
                    width: 90,
                    unit: 'em',
                    showValue: true,
                    showTooltip: true,
                    onInput({ value }) {
                        calendar.eachView(v => v.resourceWidth = value + 'em');
                    }
                }
            }
        },        
        features: {
            eventEdit: {
                showRecurringUI: false,
                items: {
                    nameField: null,
                    resourceField: null,
                    allDay: false,
                    startDateField: null,
                    startTimeField: null,
                    endDateField: null,
                    endTimeField: null,
                    resourceId: {
                        type: 'combo',
                        label: 'Profissional',
                        name: 'resourceId',
                        required: true,
                        store: profissionaisStore,
                        valueField: 'id',
                        displayField: 'text',
                        weight: 200
                    },
                    servico_id: {
                        type: 'combo',
                        label: 'Serviço',
                        name: 'servico_id',
                        required: true,
                        store: servicosStore,
                        valueField: 'id',
                        displayField: 'text',
                        weight: 300
                    },
                    cliente_id: {
                        type: 'combo',
                        label: 'Cliente',
                        name: 'cliente_id',
                        required: true,
                        store: clientesStore,
                        valueField: 'id',
                        displayField: 'text',
                        weight: 400
                    },
                    startDate: {
                        type: 'datetime',
                        label: 'Início',
                        name: 'startDate',
                        required: true,
                        weight: 500
                    },
                    endDate: {
                        type: 'datetime',
                        label: 'Fim',
                        name: 'endDate',
                        required: true,
                        weight: 600
                    },
                    valor_cobrado: {
                        type: 'number',
                        label: 'Valor Cobrado',
                        name: 'valor_cobrado',
                        required: false,
                        step: 0.01,
                        min: 0,
                        weight: 700
                    }
                }
            }
        },
        listeners: {
            beforeEventEditShow({ editor, eventRecord }) {
                console.log('Abrindo editor para evento:', eventRecord.data);

                // Validar se as stores estão preenchidas
                if (!profissionaisStore.data.length || !servicosStore.data.length || !clientesStore.data.length) {
                    console.warn('Uma ou mais stores estão vazias');
                    Toast.show({
                        html: 'Aguardando carregamento de dados. Tente novamente.',
                        timeout: 3000
                    });
                    return false; // Cancela a abertura do editor
                }

                // Definir os valores dos campos com base no eventRecord
                const resourceCombo = editor.widgetMap.resourceId;
                const servicoCombo = editor.widgetMap.servico_id;
                const clienteCombo = editor.widgetMap.cliente_id;
                const valorCobradoField = editor.widgetMap.valor_cobrado;

                if (resourceCombo && eventRecord.resourceId) {
                    resourceCombo.value = eventRecord.resourceId;
                }
                if (servicoCombo && eventRecord.servico_id) {
                    servicoCombo.value = eventRecord.servico_id;
                }
                if (clienteCombo && eventRecord.cliente_id) {
                    clienteCombo.value = eventRecord.cliente_id;
                }
                if (valorCobradoField && eventRecord.valor_cobrado != null) {
                    valorCobradoField.value = eventRecord.valor_cobrado;
                }
                
            },
            beforeEventEditSave({ editor, eventRecord }) {
                const servico_id = editor.widgetMap.servico_id.value;
                const resourceId = editor.widgetMap.resourceId.value;
                const cliente_id = editor.widgetMap.cliente_id.value;
                const valor_cobrado = editor.widgetMap.valor_cobrado.value;

                if (!servico_id || !resourceId || !cliente_id) {
                    Toast.show({
                        html: 'Por favor, selecione um profissional, serviço e cliente',
                        timeout: 3000
                    });
                    return false;
                }

                eventRecord.set({
                    servico_id: Number(servico_id),
                    resourceId: Number(resourceId),
                    cliente_id: Number(cliente_id),
                    valor_cobrado: valor_cobrado ? Number(valor_cobrado) : null,
                    name: null,
                    duration: null,
                    durationUnit: null,
                    allDay: false,
                    exceptionDates: null
                });

                return true;
            }
        }, 
    });

    window.calendar = calendar;
}).catch(error => {
    console.error('Erro ao carregar dados iniciais dos combos:', error);
    Toast.show({
        html: 'Erro ao carregar profissionais, serviços ou clientes',
        timeout: 3000
    });
});