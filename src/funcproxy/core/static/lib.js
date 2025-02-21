function showToast(message, type = 'success') {
    const iconMap = {
        success: '✅',
        error: '❌',
        info: '💡'
    };

    const container = $(`
    <div class="toast-container ${type}">
        <span class="toast-icon">${iconMap[type]}</span>
        <span>${message}</span>
        <button class="toast-close">&times;</button>
    </div>
`);

    $('body').append(container);
    container.addClass('show');

    setTimeout(() => {
        container.removeClass('show');
    }, 3000);

    container.find('.toast-close').on('click', () => {
        container.removeClass('show');
    });
}