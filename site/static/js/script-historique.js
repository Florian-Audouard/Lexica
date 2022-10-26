const urlParam = new URLSearchParams(window.location.search);
const langue = urlParam.get("langue");
const sens = urlParam.get("sens");

presentation = document.querySelector("#presentation");
presentation.innerText = `Historique du sens ${sens} en ${langue}`;

function createTable(json) {
	result = document.querySelector("#resultHistory");
	for (let line of json) {
		let tr = document.createElement("tr");

		// Date
		let td = document.createElement("td");
		const date = new Date(line[0]);
		const hours = String(date.getHours()).padStart(2, "0");
		const min = String(date.getMinutes()).padStart(2, "0");
		const seconde = String(date.getSeconds()).padStart(2, "0");
		td.innerText = `${hours}:${min}:${seconde}, ${date.toLocaleDateString(
			"fr"
		)}`;
		tr.appendChild(td);

		// traduction
		td = document.createElement("td");
		td.innerText = line[1];
		tr.appendChild(td);

		result.appendChild(tr);
	}
}

fetch("/historyRequest", {
	method: "POST",
	headers: {
		Accept: "application/json",
		"Content-Type": "application/json",
	},
	body: JSON.stringify({
		langue: langue,
		sens: sens,
	}),
})
	.then((resp) => {
		return resp.json();
	})
	.then((json) => {
		createTable(json);
	});
