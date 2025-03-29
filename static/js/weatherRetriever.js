
let openWeatherAPIString = "";

document.addEventListener("DOMContentLoaded", () => {

    const daySelector = document.getElementById("daySelector");
    const submitBtn = document.getElementById("predictButton");
    const modelSelector = document.getElementById("modelSelector");

    // Create separate instances for each future date
    const today = new Date();
    const date2 = new Date(today);
    const date3 = new Date(today);
    const date4 = new Date(today);
    const date5 = new Date(today);

    // Set the future dates
    date2.setDate(today.getDate() + 2);
    date3.setDate(today.getDate() + 3);
    date4.setDate(today.getDate() + 4);
    date5.setDate(today.getDate() + 5);

    // Format the dates as readable strings
    const secondDayString = date2.toDateString();
    const thirdDayString = date3.toDateString();
    const fourthDayString = date4.toDateString();
    const fifthDayString = date5.toDateString();

    // Assign values to HTML elements (Make sure these elements exist)
    document.getElementById("secondDay").innerHTML = secondDayString;
    document.getElementById("thirdDay").innerHTML = thirdDayString;
    document.getElementById("fourthDay").innerHTML = fourthDayString;
    document.getElementById("fifthDay").innerHTML = fifthDayString;


    // listen to Submit Event
    submitBtn.addEventListener("click", async () => {
        const selectedDate = daySelector.value;
        const model = modelSelector.value;
        console.log(selectedDate, model);
        submitBtn.disabled = true;
        submitBtn.innerHTML = "⏳ Predicting...";

        await getWeatherData(selectedDate, model);

        // After processing is complete
        submitBtn.disabled = false;
        submitBtn.innerHTML = "🔍 Predict Ventilation Time";
    });
});


// Fetch API key from Flask server
async function loadAPIKey() {
    try {
        const response = await fetch("http://127.0.0.1:5000/config");
        const data = await response.json();

        console.log("API Key Loaded:", data.openWeatherAPI);
        openWeatherAPIString = data.openWeatherAPI
    } catch (error) {
        console.error("Error fetching API key:", error);
    }
};


/**
 * The function `filterForeCastByDate` filters a list of forecast entries based on a selected date
 * (today or tomorrow).
 * @param foreCastList - An array of weather forecast entries, each containing a date and time in the
 * format "yyyy-mm-dd hh:mm:ss".
 * @param selectedDate - The `selectedDate` parameter is used to determine which date to filter the
 * `foreCastList` by. It can have the values "today" or "tomorrow" to filter the forecast entries for
 * the current day or the next day respectively. If any other value is provided, an error message
 * @returns The function `filterForeCastByDate` is returning a filtered list of entries from the
 * `foreCastList` based on the `selectedDate`. If the `selectedDate` is "today" or "tomorrow", it will
 * filter the entries that have a date matching the target date (either today's date or tomorrow's
 * date). If the `selectedDate` is neither "today" nor
 */
function filterForecastByDate(foreCastList, selectedDate) {
    const today = new Date();
    let targetDate;

    switch (selectedDate) {
        case "secondDay":
            const secondDay = new Date();
            secondDay.setDate(today.getDate() + 2);
            targetDate = secondDay.toISOString().split("T")[0]; // Format yyyy-mm-dd
            break;
        case "thirdDay":
            const thirdDay = new Date();
            thirdDay.setDate(today.getDate() + 3);
            targetDate = thirdDay.toISOString().split("T")[0];
            break;
        case "fourthDay":
            const fourthDay = new Date();
            fourthDay.setDate(today.getDate() + 4);
            targetDate = fourthDay.toISOString().split("T")[0];
            break;
        case "fifthDay":
            const fifthDay = new Date();
            fifthDay.setDate(today.getDate() + 5);
            targetDate = fifthDay.toISOString().split("T")[0];
            break;
        default:
            // Assume `selectedDate` is already a valid date string
            targetDate = selectedDate;
    }
    console.log(`Filtering forecast for date: ${targetDate}`);

    return {
        filteredForecast: foreCastList.filter(entry => entry.dt_txt.startsWith(targetDate)),
        targetDate
    };
}


/**
 * The function `getWeatherData` fetches hourly weather data for a specified location from the
 * OpenWeather API, extracts the temperatures, and sends the data to a Python backend.
 * @param params - The `params` object is not being used in the `getWeatherData` function you provided.
 * If you have specific parameters that need to be passed to this function, you can update the function
 * signature to accept those parameters and then use them within the function body.
 * @returns The `getWeatherData` function is an asynchronous function that fetches weather data from
 * the OpenWeather API for a specific city (Madrid in this case). If the OpenWeather API key is not
 * loaded, it logs an error message and returns early. It then constructs a URL with the provided
 * parameters, makes a fetch request to the API, and processes the response data.
 */
async function getWeatherData(selectedDate, model) {

    await loadAPIKey()
    if (!openWeatherAPIString) {
        console.error("API key not loaded yet.");
        return;
    }

    let CITY = "Madrid"; // Change to your location
    const UNITS = "metric"; // Change to your location
    const url = `https://api.openweathermap.org/data/2.5/forecast?q=${CITY}&units=${UNITS}&appid=${openWeatherAPIString}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        console.log(data);

        if (data.cod === "200") {
            // ✅ Extract forecast for the selected day
            const { filteredForecast, targetDate } = filterForecastByDate(data.list, selectedDate);
            // Debugging:
            console.log("Filtered Forecast for", targetDate, ":", filteredForecast.length);

            // send data to python backend
            await sendToBackEnd(filteredForecast, targetDate, model)

        } else {
            throw new Error(data.message);
        }
    }
    catch (error) {
        console.error("Error fetching weather data", error);
    }
}


/**
 * The function `sendToBackEnd` asynchronously sends weather data to a backend server and logs the best
 * time received in the response.
 * @param weatherData - The `weatherData` parameter in the `sendToBackEnd` function is the data related
 * to weather that you want to send to the backend server for processing. This data should be in JSON
 * format and will be included in the body of the POST request to the backend server. The backend
 * server will
 */
async function sendToBackEnd(filteredForecast, targetDate, model) {

    console.log("Sending to backend:", { filteredForecast, targetDate });
    try {
        const response = await fetch("http://127.0.0.1:5000/process_weather", { // Adjust URL if using FastAPI
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                weatherData: filteredForecast,
                targetDate: targetDate,
                model: model
            })
        });

        const result = await response.json();
        console.log("Best Ventilation Time:", result.bestVentilationTime);
        console.log("Alternative Times:", result.alternativeTimes);

        const alternatives = Array.isArray(result.alternativeTimes)
            ? result.alternativeTimes.join(', ')
            : "No alternatives available";

        sendVisualResults(result, alternatives, targetDate)

    }
    catch (error) {
        console.error("Error sending data to backend:", error);
    }


    /**
     * The function `sendVisualResults` displays weather-related data in the DOM and updates the
     * weather icon based on the weather condition provided.
     * @param result - The `sendVisualResults` function is designed to display weather-related results
     * in the DOM based on the `result` object passed to it. The `result` object contains the following
     * properties:
     */
    async function sendVisualResults(result, alternatives) {
        // Display in DOM
        document.getElementById("result-container").style.display = "block";
        document.getElementById("avgTemp").textContent = result.avgTemperature;
        document.getElementById("minTemp").textContent = result.minTemperature;
        document.getElementById("maxTemp").textContent = result.maxTemperature;
        document.getElementById("bestVentilationTime").textContent = result.bestVentilationTime;
        document.getElementById("morningSuggestion").textContent = result.morningSuggestion;
        document.getElementById("eveningSuggestion").textContent = result.eveningSuggestion;
        document.getElementById("alternativeTimes").textContent = alternatives;
        document.getElementById("season").textContent = result.season;

        updateWeatherIcon(result.weatherCondition)
    }




   /**
    * The function `updateWeatherIcon` takes a weather condition as input and updates the weather icon
    * and description on a webpage based on the condition.
    * @param weatherCondition - The `weatherCondition` parameter should be a string representing the
    * current weather condition. It can be one of the following values: "clear", "clouds", "rain",
    * "drizzle", "thunderstorm", or "snow".
    */
    function updateWeatherIcon(weatherCondition) {
        const iconMap = {
        clear: {
            icon: "clear.png",
            description: "Clear sky"
        },
        clouds: {
            icon: "clouds.png",
            description: "Cloudy"
        },
        rain: {
            icon: "rain.png",
            description: "Rainy"
        },
        drizzle: {
            icon: "drizzle.png",
            description: "Light rain"
        },
        thunderstorm: {
            icon: "thunderstorm.png",
            description: "Stormy"
        },
        snow: {
            icon: "snow.png",
            description: "Snowy"
        }
          }
    

    const lowerCondition = weatherCondition.toLowerCase();
    const info = iconMap[lowerCondition];

    // Fallback if condition is not mapped
    const iconFile = info ? info.icon : "Ups!";
    const description = info ? info.description : "Unknown Weather Category";

    document.getElementById("weatherCondition").textContent = description;
    document.getElementById("weather-icon").src = `/static/images/${iconFile}`;
    }

}