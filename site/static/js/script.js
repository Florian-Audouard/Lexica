let input = document.querySelector("#search");

function listeDesLangue() {
	let res = [
		"français",
		"pije",
		"fwâi",
		"nemi 1 (Temala)",
		"nemi 2 (côte est)",
		"jawe",
	];
	return res;
}

function createTableResult(tab) {
	let listeLangue = listeDesLangue();
	let resultBox = document.querySelector("#result");
	resultBox.innerHTML = "";
	let trTitle = document.createElement("tr");
	for (let langue of listeLangue) {
		let th = document.createElement("th");
		th.innerHTML = langue;
		trTitle.appendChild(th);
	}
	resultBox.appendChild(trTitle);
	for (let ligne of tab) {
		let tr = document.createElement("tr");
		for (let langue of listeLangue) {
			let th = document.createElement("th");
			if (ligne.has(langue)) {
				th.innerHTML = ligne.get(langue);
			}
			tr.appendChild(th);
		}
		resultBox.appendChild(tr);
	}
}

function arrayToObject(arr) {
	let res = [];
	for (let ligne of arr) {
		tmp = new Map();
		for (let element of ligne) {
			tmp.set(element[0], element[1]);
		}
		res.push(tmp);
	}
	return res;
}

document.querySelector("#searchButton").addEventListener("click", (_) => {
	let keyword = input.value;
	if (keyword !== "") {
		fetch("/search", {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				keyword: keyword.toLowerCase(),
			}),
		})
			.then((resp) => {
				return resp.json();
			})
			.then((json) => {
				createTableResult(arrayToObject(json));
			});
	}
});
