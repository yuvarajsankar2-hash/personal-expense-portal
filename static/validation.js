document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', (event) => {
        const amount = form.querySelector('[name="amount"]');
        if (amount && Number(amount.value) <= 0) {
            event.preventDefault();
            alert('Amount must be greater than zero.');
        }
    });
});
