/**
 * Recantos dos Pinheiros — Forms
 * Validação client-side, submit via fetch, máscaras
 */

document.addEventListener('DOMContentLoaded', () => {
    initReservaForm();
    initContatoForm();
    initPhoneMask();
});

/* ─── Máscara de Telefone ───────────────────────────────────── */
function initPhoneMask() {
    const phoneInput = document.getElementById('telefone');
    if (!phoneInput) return;

    phoneInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');

        if (value.length <= 2) {
            value = `(${value}`;
        } else if (value.length <= 6) {
            value = `(${value.substring(0, 2)}) ${value.substring(2)}`;
        } else if (value.length <= 10) {
            value = `(${value.substring(0, 2)}) ${value.substring(2, 6)}-${value.substring(6)}`;
        } else {
            value = `(${value.substring(0, 2)}) ${value.substring(2, 7)}-${value.substring(7, 11)}`;
        }

        e.target.value = value;
    });
}

/* ─── Formulário de Reserva ─────────────────────────────────── */
function initReservaForm() {
    const form = document.getElementById('reservaForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('submitReserva');
        const originalText = submitBtn.innerHTML;

        // Validação
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const dataEvento = form.data_evento.value;
        if (!dataEvento) {
            showToast('Por favor, selecione uma data no calendário.', 'error');
            return;
        }

        // Loading state
        submitBtn.innerHTML = '<span class="spinner"></span> Enviando...';
        submitBtn.classList.add('btn--loading');

        try {
            // Coletar serviços
            const servicos = Array.from(form.querySelectorAll('input[name="servicos"]:checked'))
                .map(cb => cb.value);

            const payload = {
                nome: form.nome.value.trim(),
                email: form.email.value.trim(),
                telefone: form.telefone.value.replace(/\D/g, ''),
                data_evento: dataEvento,
                tipo_evento: form.tipo_evento.value,
                num_convidados: parseInt(form.num_convidados.value, 10),
                horario_inicio: form.horario_inicio.value,
                horario_fim: form.horario_fim.value,
                servicos_adicionais: servicos,
                observacoes: form.observacoes.value.trim(),
            };

            const response = await fetch('/api/reservas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                showToast('Pré-reserva pronta! Redirecionando para o WhatsApp...', 'success');
                // Redirect to WhatsApp Flow
                setTimeout(() => {
                    if (data.whatsapp_link) {
                        window.location.href = data.whatsapp_link;
                    } else {
                        window.location.href = '/';
                    }
                }, 1500);
            } else {
                showToast(data.detail || 'Erro ao enviar reserva.', 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.classList.remove('btn--loading');
        }
    });
}

/* ─── Formulário de Contato ─────────────────────────────────── */
function initContatoForm() {
    const form = document.getElementById('contatoForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('submitContato');
        const originalText = submitBtn.innerHTML;

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        submitBtn.innerHTML = '<span class="spinner"></span> Enviando...';
        submitBtn.classList.add('btn--loading');

        try {
            const payload = {
                nome: form.nome.value.trim(),
                email: form.email.value.trim(),
                mensagem: form.mensagem.value.trim(),
            };

            const response = await fetch('/api/contato', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok) {
                showToast('Mensagem enviada com sucesso! Retornaremos em breve.', 'success');
                form.reset();
            } else {
                showToast(data.detail || 'Erro ao enviar mensagem.', 'error');
            }
        } catch (error) {
            console.error('Erro:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.classList.remove('btn--loading');
        }
    });
}
