/**
 * Recantos dos Pinheiros — Calendar Component
 * Calendário interativo com fetch de disponibilidade via API
 */

document.addEventListener('DOMContentLoaded', () => {
    const calDays = document.getElementById('calDays');
    if (!calDays) return;

    const calTitle = document.getElementById('calTitle');
    const calPrev = document.getElementById('calPrev');
    const calNext = document.getElementById('calNext');
    const dataEventoInput = document.getElementById('data_evento');

    const MONTHS = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    let currentDate = new Date();
    let selectedDate = null;
    let unavailableDates = [];

    // Init
    renderCalendar();

    // Navigation
    calPrev.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    calNext.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    async function renderCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        calTitle.textContent = `${MONTHS[month]} ${year}`;

        // Fetch disponibilidade
        await fetchAvailability(year, month + 1);

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        calDays.innerHTML = '';

        // Dias vazios antes do primeiro dia
        for (let i = 0; i < firstDay; i++) {
            const empty = document.createElement('div');
            empty.className = 'calendar__day calendar__day--empty';
            calDays.appendChild(empty);
        }

        // Dias do mês
        for (let day = 1; day <= daysInMonth; day++) {
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar__day';
            dayEl.textContent = day;

            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const dateObj = new Date(year, month, day);

            // Passado
            if (dateObj < today) {
                dayEl.classList.add('calendar__day--disabled');
            }
            // Indisponível
            else if (unavailableDates.includes(dateStr)) {
                dayEl.classList.add('calendar__day--unavailable');
                dayEl.title = 'Data ocupada';
            }
            // Disponível
            else {
                dayEl.classList.add('calendar__day--available');
                dayEl.title = 'Clique para selecionar';
                dayEl.addEventListener('click', () => selectDate(dateStr, dayEl));
            }

            // Hoje
            if (dateObj.toDateString() === today.toDateString()) {
                dayEl.classList.add('calendar__day--today');
            }

            // Selecionado
            if (selectedDate === dateStr) {
                dayEl.classList.add('calendar__day--selected');
            }

            calDays.appendChild(dayEl);
        }
    }

    function selectDate(dateStr, element) {
        selectedDate = dateStr;

        // Visual
        calDays.querySelectorAll('.calendar__day--selected').forEach(el => {
            el.classList.remove('calendar__day--selected');
        });
        element.classList.add('calendar__day--selected');

        // Preencher input do formulário
        if (dataEventoInput) {
            dataEventoInput.value = dateStr;
        }

        // Scroll para formulário em mobile
        if (window.innerWidth < 768) {
            const form = document.getElementById('reservaForm');
            if (form) {
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        // Feedback visual
        if (typeof showToast === 'function') {
            const parts = dateStr.split('-');
            showToast(`Data selecionada: ${parts[2]}/${parts[1]}/${parts[0]}`, 'info', 2000);
        }
    }

    async function fetchAvailability(year, month) {
        try {
            const response = await fetch(`/api/disponibilidade?year=${year}&month=${month}`);
            if (!response.ok) throw new Error('Erro ao buscar disponibilidade');

            const data = await response.json();
            unavailableDates = data.unavailable_dates || [];
        } catch (error) {
            console.error('Erro ao buscar disponibilidade:', error);
            unavailableDates = [];
        }
    }
});
