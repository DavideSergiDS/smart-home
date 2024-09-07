import { Bot, InlineKeyboard } from "grammy";
import {
  TelemetrySample,
  TelemetrySource,
  getTelemetryTargets,
} from "./Telemetry";

//Store bot screaming status
let telemetrySource: TelemetrySource | null = null;
let telemetryInterval: NodeJS.Timeout | null = null;

//Create a new bot
const bot = new Bot("7441382040:AAG-cv8xOXzhyCfS8AqgbiA0P2xyueuWvds");

// Set command
bot.api.setMyCommands([
  { command: "telemetry", description: "Monitor telemetry data." },
]);

// Set command: 1. Define menu text
const targetSelectionMenuText =
  "<b>Target selection</b>\n\nSelect the target you want to monitor.";

// Set command: 2. Build keyboards
const startButton = "Start";
const dismissButton = "Dismiss";
const backButton = "Back";
const stopButton = "Stop";

const targetSelectionMenuMarkup = new InlineKeyboard()
  .text(dismissButton, dismissButton)
  .text(startButton, startButton);

const telemetryMenuMarkup = new InlineKeyboard()
  .text(backButton, backButton)
  .text(stopButton, stopButton);

const stoppedTelemetryMenuMarkup = new InlineKeyboard().text(
  backButton,
  backButton
);

// Set command: 3. Define handler
bot.command("telemetry", async (ctx) => {
  await ctx.reply(targetSelectionMenuText, {
    parse_mode: "HTML",
    reply_markup: targetSelectionMenuMarkup,
  });
});

bot.callbackQuery(dismissButton, async (ctx) => {
  await ctx.deleteMessage();
});

//This handler processes back button on the menu
bot.callbackQuery(backButton, async (ctx) => {
  telemetrySource?.stop();
  telemetrySource = null;
  clearInterval(telemetryInterval || undefined);
  telemetryInterval = null;
  await ctx.editMessageText(targetSelectionMenuText, {
    reply_markup: targetSelectionMenuMarkup,
    parse_mode: "HTML",
  });
});

//This handler processes stop button on the menu
bot.callbackQuery(stopButton, async (ctx) => {
  telemetrySource?.stop();
  telemetrySource = null;
  clearInterval(telemetryInterval || undefined);
  telemetryInterval = null;
  await ctx.editMessageText("<b>Data streaming stopped.</b>", {
    reply_markup: stoppedTelemetryMenuMarkup,
    parse_mode: "HTML",
  });
});

//This handler processes next button on the menu
bot.callbackQuery(startButton, async (ctx) => {
  const telemetryTarget = (await getTelemetryTargets())[0];
  telemetrySource = new TelemetrySource(telemetryTarget);

  telemetryInterval = setInterval(
    () => {
      const telemetry = telemetrySource?.start().next()
        .value as TelemetrySample;
      console.log(telemetrySource?.start().next().value);
      ctx.editMessageText(
        `<b>${telemetry?.label} is ${(telemetry?.value as number).toFixed(2)} ${
          telemetry?.unit
        } in the ${telemetrySource?.target.label}</b>`,
        {
          reply_markup: telemetryMenuMarkup,
          parse_mode: "HTML",
        }
      );
    },

    1000
  );
  await ctx.editMessageText("<b>Retrieving data...</b>", {
    parse_mode: "HTML",
    reply_markup: telemetryMenuMarkup,
  });
});

//This function would be added to the dispatcher as a handler for messages coming from the Bot API
bot.on("message", async (ctx) => {
  //Print to console
  console.log(
    `${ctx.from.first_name} wrote ${
      "text" in ctx.message ? ctx.message.text : ""
    }`
  );

  // if (ctx.message.text) {
  //   //Scream the message
  //   await ctx.reply(ctx.message.text.toUpperCase(), {
  //     entities: ctx.message.entities,
  //   });
  // } else {
  //   //This is equivalent to forwarding, without the sender's name
  //   await ctx.copyMessage(ctx.message.chat.id);
  // }
});

//Start the Bot
bot.start();
