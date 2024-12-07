document.addEventListener('DOMContentLoaded', function () {
    const darkModeSwitch = document.getElementById('darkModeSwitch');
    const body = document.body;

    // Load previous dark mode preference from local storage
    const darkModeEnabled = localStorage.getItem('darkMode') === 'true';
    if (darkModeEnabled) {
        body.classList.add('dark-mode');
    }

    // Toggle dark mode
    darkModeSwitch.addEventListener('click', function () {
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
    });

    // Fetch and populate available dates for the dropdown
    const dateDropdown = document.getElementById('date');
    fetch('/available-dates')
        .then(response => response.json())
        .then(dates => {
            dates.forEach(date => {
                const option = document.createElement('option');
                option.value = date;
                option.textContent = date;
                dateDropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching dates:', error);
        });

    // Handle the booking form submission
    const bookingForm = document.getElementById('bookingForm');
    bookingForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const fullName = document.getElementById('fullName').value;
        const room = document.getElementById('room').value;
        const bookingDate = dateDropdown.value;
        const agreeRules = document.getElementById('agreeRules').checked; // Check if the rules are agreed to

        if (!fullName || !room || !bookingDate || !agreeRules) {
            alert("Please fill in all fields and agree to the rules.");
            return;
        }

        // Send the booking request to the server
        fetch('/book-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fullName: fullName,
                title: room,
                start: bookingDate,
            }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Booking successful');
                    location.reload(); // Reload to update the table
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while booking the room.');
            });
    });
});
