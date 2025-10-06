/* jshint esversion: 11 */

// Ensure event date is not before "today"
// Suggested by Mentor Tim Nelson
let now = new Date(),
    minDate = now.toISOString().substring(0, 10);
document.getElementById("id_date").setAttribute("min", minDate);