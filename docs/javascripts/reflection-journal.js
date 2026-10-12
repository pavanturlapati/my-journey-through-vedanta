/*
 * Reflection journal.
 *
 * Turns the numbered list of questions just above a <div class="reflection-journal">
 * into answer boxes, saves answers in this browser only (localStorage), and opens
 * a print-friendly page the reader can save as a PDF. Nothing is sent anywhere.
 *
 * Usage in a page (after the <ol> of questions):
 *   <div class="reflection-journal" data-key="navaratri-day-1"
 *        data-title="Day 1 of Navaratri: ..."
 *        data-hints="hint for Q1|hint for Q2|..."></div>
 *
 * Questions are every numbered list between the section's H2 and the div. An H4
 * directly above a list names its group. data-hints is optional: one short
 * generic example per question, separated by |, shown as grey placeholder text
 * that disappears when the reader types. It is never saved or put in the PDF.
 */
(function () {
  "use strict";

  var STORE = "rj:";

  var LLM_NOTE =
    "These are one person's personal reflections written for contemplation. " +
    "Please read each answer with care and respond with gentle, thoughtful " +
    "feedback: what stands out, patterns you notice, and follow-up questions " +
    "worth exploring. This is not a test. Do not give legal, medical, " +
    "psychological or professional advice. Where an answer says \"I don't know " +
    "yet\", treat that as a valid answer.";

  var DISCLAIMER =
    "The questions are suggestions for personal reflection only. They are not " +
    "legal, medical, psychological or professional advice, and they are not a " +
    "test or assessment. The author of this website did not collect and does " +
    "not have these answers.";

  var COPY_PROMPT =
    "I have attached a PDF of my personal reflections on a set of questions. " +
    "Please read my answers and give me gentle, thoughtful feedback: what " +
    "stands out, any patterns you notice, and a few follow-up questions I " +
    "could explore. This is for personal reflection, not professional advice.";

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function load(key) {
    try {
      return JSON.parse(localStorage.getItem(STORE + key)) || {};
    } catch (e) {
      return {};
    }
  }

  function save(key, data) {
    try {
      localStorage.setItem(STORE + key, JSON.stringify(data));
    } catch (e) {
      /* storage unavailable (private mode, blocked): answers just aren't saved */
    }
  }

  function wipe(key) {
    try {
      localStorage.removeItem(STORE + key);
    } catch (e) {}
  }

  function findQuestions(box) {
    /* Collect every numbered list between the previous H1/H2 and the box, in order.
       An H4 directly above a list names its group. */
    var lists = [];
    var el = box.previousElementSibling;
    while (el && !/^H[12]$/.test(el.tagName)) {
      if (el.tagName === "OL") lists.unshift(el);
      el = el.previousElementSibling;
    }
    var out = [];
    lists.forEach(function (ol) {
      ol.setAttribute("start", String(out.length + 1));
      var prev = ol.previousElementSibling;
      var group = prev && prev.tagName === "H4" ? prev.textContent.replace(/\u00b6/g, "").trim() : "";
      Array.prototype.forEach.call(ol.querySelectorAll(":scope > li"), function (li) {
        var strong = li.querySelector("strong");
        out.push({
          short: strong ? strong.textContent.trim() : li.textContent.trim(),
          full: li.textContent.trim(),
          group: group,
        });
      });
    });
    return out;
  }

  function buildPrintHtml(title, questions, answers) {
    var date = new Date().toLocaleDateString(undefined, {
      year: "numeric", month: "long", day: "numeric",
    });
    var lastGroup = "";
    var body = questions.map(function (q, i) {
      var a = (answers[i] || "").trim();
      var head = "";
      if (q.group && q.group !== lastGroup) head = "<h3 class='g'>" + esc(q.group) + "</h3>";
      lastGroup = q.group;
      return (
        head +
        "<section><h2>" + (i + 1) + ". " + esc(q.short) + "</h2>" +
        "<p class='q'>" + esc(q.full.replace(q.short, "").trim()) + "</p>" +
        "<p class='a'>" + (a ? esc(a).replace(/\n/g, "<br>") : "<em>(not answered)</em>") + "</p></section>"
      );
    }).join("");

    return (
      "<!doctype html><html><head><meta charset='utf-8'><title>" + esc(title) + " - My reflections</title>" +
      "<style>" +
      "body{font-family:Georgia,'Times New Roman',serif;max-width:42rem;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#111}" +
      "h1{font-size:1.5rem;margin-bottom:.2rem}h2{font-size:1.1rem;margin:1.6rem 0 .2rem}" +
      "h3.g{font-size:1rem;text-transform:uppercase;letter-spacing:.05em;color:#555;border-bottom:1px solid #ccc;padding-bottom:.2rem;margin:2rem 0 0}" +
      ".meta{color:#555;margin-top:0}.q{color:#555;font-size:.92rem;margin:.1rem 0 .5rem}" +
      ".a{border-left:3px solid #999;padding-left:.8rem;margin:.3rem 0}" +
      ".note{border:1px solid #bbb;border-radius:4px;padding:.7rem 1rem;margin:1.2rem 0;font-size:.92rem;background:#f6f6f6}" +
      ".bar{margin:1rem 0;padding:.7rem 1rem;background:#fff4d6;border:1px solid #e0c36a;font-family:system-ui,sans-serif;font-size:.9rem}" +
      "button{font-size:1rem;padding:.4rem .9rem;margin-right:.5rem}" +
      "@media print{.bar{display:none}body{margin:0;max-width:none}}" +
      "</style></head><body>" +
      "<div class='bar'>To save a PDF: click <button onclick='window.print()'>Print</button> and choose " +
      "<strong>Save as PDF</strong> as the destination. This bar will not appear in the PDF.</div>" +
      "<h1>My reflections</h1><p class='meta'>" + esc(title) + "<br>" + esc(date) + "</p>" +
      "<div class='note'><strong>Note for an AI assistant:</strong> " + esc(LLM_NOTE) + "</div>" +
      body +
      "<div class='note'><strong>Disclaimer:</strong> " + esc(DISCLAIMER) + "</div>" +
      "</body></html>"
    );
  }

  function init(box) {
    var key = box.getAttribute("data-key");
    var title = box.getAttribute("data-title") || document.title;
    var hints = (box.getAttribute("data-hints") || "").split("|");
    var questions = findQuestions(box);
    if (!key || !questions.length) return;

    var answers = load(key);
    var html = "";

    html += "<h3>Write your reflections</h3>";
    html +=
      "<div class='rj-steps'><ol>" +
      "<li>Answer one or more questions below. “I don't know yet” is a valid answer.</li>" +
      "<li>Click <strong>Open print-friendly page</strong>, then choose <strong>Save as PDF</strong> in the print dialog.</li>" +
      "<li>Upload the PDF to your own AI assistant and ask for feedback. You can copy a suggested prompt below.</li>" +
      "</ol></div>";

    html +=
      "<div class='admonition warning'><p class='admonition-title'>Please read</p>" +
      "<p><strong>I do not receive your answers.</strong> They stay in your browser on this device. " +
      "They are saved here only so a refresh does not lose them, and you can clear them at any time.</p>" +
      "<p>These questions are suggestions for personal reflection only. They are not legal, medical, " +
      "psychological or professional advice, and they are not a test or an assessment. " +
      "If you share your PDF with an AI assistant, that provider handles it under its own privacy terms, " +
      "and its feedback can be wrong. Please do not include sensitive personal details.</p></div>";

    var lastGroupShown = "";
    questions.forEach(function (q, i) {
      if (q.group && q.group !== lastGroupShown) {
        html += "<h4 class='rj-group'>" + esc(q.group) + "</h4>";
      }
      lastGroupShown = q.group;
      var hint = (hints[i] || "").trim();
      html +=
        "<div class='rj-q'><label for='rj-" + esc(key) + "-" + i + "'>" +
        "<strong>" + (i + 1) + ". " + esc(q.short) + "</strong></label>" +
        "<textarea id='rj-" + esc(key) + "-" + i + "' data-i='" + i + "' rows='4'" +
        (hint ? " placeholder='" + esc("Example: " + hint) + "'" : "") +
        "></textarea></div>";
    });

    html +=
      "<div class='rj-actions'>" +
      "<button type='button' class='md-button md-button--primary' data-act='print'>Open print-friendly page</button> " +
      "<button type='button' class='md-button' data-act='copy'>Copy suggested AI prompt</button> " +
      "<button type='button' class='md-button' data-act='clear'>Clear my answers</button>" +
      "<p class='rj-status' role='status' aria-live='polite'></p></div>";

    box.innerHTML = html;

    var status = box.querySelector(".rj-status");
    function say(msg) { status.textContent = msg; }

    Array.prototype.forEach.call(box.querySelectorAll("textarea"), function (ta) {
      var i = ta.getAttribute("data-i");
      if (answers[i]) ta.value = answers[i];
      ta.addEventListener("input", function () {
        answers[i] = ta.value;
        save(key, answers);
      });
    });

    box.addEventListener("click", function (e) {
      var act = e.target && e.target.getAttribute && e.target.getAttribute("data-act");
      if (!act) return;

      if (act === "print") {
        var w = window.open("", "_blank");
        if (!w) {
          say("Your browser blocked the new window. Please allow pop-ups for this site and try again.");
          return;
        }
        w.document.open();
        w.document.write(buildPrintHtml(title, questions, answers));
        w.document.close();
        say("Opened in a new tab. Use Print, then Save as PDF.");
      } else if (act === "copy") {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(COPY_PROMPT).then(
            function () { say("Prompt copied."); },
            function () { say("Could not copy. Please select and copy the prompt manually."); }
          );
        } else {
          say("Copying is not available in this browser.");
        }
      } else if (act === "clear") {
        if (window.confirm("Clear all your answers on this page? This cannot be undone.")) {
          answers = {};
          wipe(key);
          Array.prototype.forEach.call(box.querySelectorAll("textarea"), function (ta) { ta.value = ""; });
          say("Your answers have been cleared.");
        }
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    Array.prototype.forEach.call(document.querySelectorAll(".reflection-journal"), init);
  });
})();
