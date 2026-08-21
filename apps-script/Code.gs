function onHomepage(e) {
  return buildHomeCard();
}

function buildHomeCard() {
  var questionInput = CardService.newTextInput()
    .setFieldName("question")
    .setTitle("Ask a policy question")
    .setHint("Example: What is the password policy?");

  var askButton = CardService.newTextButton()
    .setText("Ask")
    .setOnClickAction(
      CardService.newAction()
        .setFunctionName("askPolicy")
    );

  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("Policy Assistant")
        .setSubtitle("Ask questions about policies")
    )
    .addSection(
      CardService.newCardSection()
        .addWidget(questionInput)
        .addWidget(askButton)
    )
    .build();

  return card;
}


function askPolicy(e) {
  var question =
    e.commonEventObject.formInputs.question.stringInputs.value[0];

  // Your FastAPI backend
  var backendUrl = "https://civil-pampers-pedicure.ngrok-free.dev/api/chat";

  var payload = {
    question: question
  };

  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(backendUrl, options);

    var statusCode = response.getResponseCode();
    var responseText = response.getContentText();

    if (statusCode !== 200) {
      return showErrorCard(
        "Backend error (" + statusCode + "):<br>" +
        responseText
      );
    }

    var data = JSON.parse(responseText);

    var answer = data.answer || "No answer received.";

    var sources = data.sources || [];

    var sourcesText = "";

    if (sources.length > 0) {
      sourcesText =
        "<br><br><b>Sources:</b><br>" +
        sources.join("<br>");
    }

    var responseCard = CardService.newCardBuilder()
      .setHeader(
        CardService.newCardHeader()
          .setTitle("Policy Assistant")
      )
      .addSection(
        CardService.newCardSection()
          .addWidget(
            CardService.newTextParagraph()
              .setText(
                "<b>Your question:</b><br>" +
                escapeHtml(question) +
                "<br><br>" +
                "<b>Answer:</b><br>" +
                escapeHtml(answer) +
                sourcesText
              )
          )
      )
      .build();

    return CardService.newActionResponseBuilder()
      .setNavigation(
        CardService.newNavigation().pushCard(responseCard)
      )
      .build();

  } catch (error) {
    return showErrorCard(
      "Could not connect to the Policy Assistant backend.<br><br>" +
      escapeHtml(error.toString())
    );
  }
}


function showErrorCard(message) {
  var card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("Policy Assistant")
    )
    .addSection(
      CardService.newCardSection()
        .addWidget(
          CardService.newTextParagraph()
            .setText("<b>Error:</b><br>" + message)
        )
    )
    .build();

  return CardService.newActionResponseBuilder()
    .setNavigation(
      CardService.newNavigation().pushCard(card)
    )
    .build();
}


function escapeHtml(text) {
  if (!text) {
    return "";
  }

  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function authorizeUrlFetch() {
  UrlFetchApp.fetch("https://www.google.com");
}
