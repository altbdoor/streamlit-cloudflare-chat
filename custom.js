/** @type {Document} */
const parent = window.parent.document;

const modelOptions = [
  "@cf/meta/llama-2-7b-chat-fp16",
  "@cf/meta/llama-2-7b-chat-int8",
  "@cf/mistral/mistral-7b-instruct-v0.1",
  "@hf/thebloke/llama-2-13b-chat-awq",
  "@hf/thebloke/mistral-7b-instruct-v0.1-awq",
];

/** @type {HTMLInputElement} */
const modelField = parent.querySelector('input[placeholder="Model"]');
modelField.setAttribute("list", "model-options");

/** @type {HTMLDataListElement} */
const datalistElem = parent.createElement("datalist");
datalistElem.id = "model-options";

modelOptions.forEach((item) => {
  /** @type {HTMLOptionElement} */
  const modelOptionsOpt = parent.createElement("option");
  modelOptionsOpt.value = item;
  modelOptionsOpt.textContent = item;
  datalistElem.appendChild(modelOptionsOpt);
});
modelField.parentElement.appendChild(datalistElem);
