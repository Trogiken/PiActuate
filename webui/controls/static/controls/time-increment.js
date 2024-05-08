function incrementTime() {
    // Get the current time from the element's text content
    const currentTimeElement = document.getElementById('current-time')
    if (!currentTimeElement) {
        return; // No current time element, so do nothing
    }

    const currentTime = currentTimeElement.textContent;

    // Split the time into hours and minutes
    const [hours, minutes] = currentTime.split(':').map(Number);

    // Increment the minutes by 1
    const newMinutes = (minutes + 1) % 60;

    // Increment the hours if necessary
    const newHours = hours + Math.floor((minutes + 1) / 60);

    // Format the new time as a string
    const newTime = `${newHours.toString().padStart(2, '0')}:${newMinutes.toString().padStart(2, '0')}`;

    // Update the current-time element with the new time
    currentTimeElement.textContent = newTime;
}

// Call the incrementTime function every minute
setInterval(incrementTime, 60000);
