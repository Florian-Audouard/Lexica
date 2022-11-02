export function createTableResult(
	tab,
	langueBase,
	listeLangue,
	resultTitle,
	resultSearch
) {
	let editButton = document.querySelector("#edit");
	let sendButton = document.querySelector("#send");
	editButton.hidden = false;
	sendButton.hidden = false;
	resultTitle.innerHTML = "";
	let trTitle = document.createElement("tr");
	let th;
	for (let langue of listeLangue) {
		th = document.createElement("th");
		th.innerHTML = langue;
		trTitle.appendChild(th);
	}
	th = document.createElement("th");
	th.innerHTML = "page";
	trTitle.appendChild(th);

	resultTitle.appendChild(trTitle);
	resultSearch.innerHTML = "";
	for (let ligne of tab) {
		let tr = document.createElement("tr");
		let [obj] = ligne.values();
		let sens = obj.sens;
		let td;
		for (let langue of listeLangue) {
			td = document.createElement("td");
			if (ligne.has(langue)) {
				td.innerHTML = `<a class="linkHistory" target="_blank" rel="noopener noreferrer" href="historique?sens=${sens}&langue=${langue}">${
					ligne.get(langue).text
				}</a>`;
			}
			td.sens = sens;
			td.langue = langue;
			tr.appendChild(td);
		}
		td = document.createElement("td");
		console.log(ligne);
		let num = ligne.get(langueBase).numeroPage;

		td.innerHTML = `<a class="linkPdf" target="_blank" rel="noopener noreferrer" href="static/pdf/hienghene-Fr.pdf#page=${num}">${num}</a>`;
		tr.appendChild(td);

		resultSearch.appendChild(tr);
	}
}
export function arrayToObject(arr) {
	let tab = [];
	let currentSens = -1;
	let tmp = undefined;
	for (let element of arr) {
		if (element[2] !== currentSens) {
			currentSens = element[2];
			if (tmp !== undefined) {
				tab.push(tmp);
			}
			tmp = new Map();
		}

		tmp.set(element[0], {
			text: element[1],
			sens: element[2],
			numeroPage: element[3],
		});
	}
	tab.push(tmp);
	return tab;
}
let saveChange = new Map();

export function resetSaveChange() {
	saveChange = new Map();
}

export function mapToArray() {
	let res = [];
	for (let sens of saveChange) {
		let reelSens = sens[0];
		for (let element of sens[1]) {
			res.push(element.concat([reelSens]));
		}
	}
	return res;
}

export function sendButtonInit(sendButton) {
	sendButton.addEventListener("click", (_) => {
		fetch("/edit", {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json",
			},
			body: JSON.stringify(mapToArray()),
		});
	});
}
export function listernerOnchangeTable(table) {
	table.addEventListener("keyup", (event) => {
		if (event.target.tagName.toLowerCase() === "td") {
			let sens = event.target.sens;
			let langue = event.target.langue;
			let text = event.target.innerText;
			if (!saveChange.has(sens)) {
				saveChange.set(sens, new Map());
			}
			saveChange.get(sens).set(langue, text);
		}
	});
}

export function editableTable(editButton) {
	editButton.addEventListener("click", (_) => {
		for (let th of document.querySelectorAll("td")) {
			th.contentEditable = true;
		}
	});
}
