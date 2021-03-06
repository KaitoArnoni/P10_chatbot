# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions

from botbuilder.dialogs.choices import Choice, ChoiceFactoryOptions
from botbuilder.schema import InputHints


from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.from_city_step,
                self.to_city_step,
                self.from_dt_step,
                self.to_dt_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)

        
        
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        
        self.add_dialog(
            DateResolverDialog(
                DateResolverDialog.__name__ + "_from_dt",
                self.telemetry_client,
                "When do you want to leave?"
            )
        )
        self.add_dialog(
            DateResolverDialog(
                DateResolverDialog.__name__ + "_to_dt",
                self.telemetry_client,
                "When do you want to come back?"
            )
        )
        
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    

    async def from_city_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for from_city."""
        booking_details = step_context.options

        if not booking_details.from_city:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )

        return await step_context.next(booking_details.from_city)

    async def to_city_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for to_city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.from_city = step_context.result

        if not booking_details.to_city:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )

        return await step_context.next(booking_details.to_city)

    async def from_dt_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.to_city = step_context.result

        if not booking_details.from_dt:
            return await step_context.begin_dialog(
                DateResolverDialog.__name__ + "_from_dt", booking_details.from_dt
            )

        return await step_context.next(booking_details.from_dt)

    async def to_dt_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel date.
        This will use the DATE_RESOLVER_DIALOG."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.from_dt = step_context.result

        if not booking_details.to_dt:
            return await step_context.begin_dialog(
                DateResolverDialog.__name__ + "_to_dt", booking_details.to_dt
            )

        return await step_context.next(booking_details.to_dt)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for budget."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.to_dt = step_context.result

        if not booking_details.budget:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is your maximum budget?")
                ),
            )

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result

        msg = (
            "Please confirm the following information:\n"
            "- You want to **book a flight**.\n"
            f"- From **{booking_details.from_city}** to **{booking_details.to_city}**.\n"
            f"- Between the **{booking_details.from_dt}** and the **{booking_details.to_dt}**.\n"
            f"- With a budget of **{booking_details.budget}**."
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction, track data and end the dialog."""

        booking_details = step_context.options

        # Create data to track in App Insights
        properties = {}
        properties["from_city"] = booking_details.from_city
        properties["to_city"] = booking_details.to_city
        properties["from_dt"] = booking_details.from_dt
        properties["to_dt"] = booking_details.to_dt
        properties["budget"] = booking_details.budget

        
        # If the BOT is successful
        if step_context.result:
            # Track YES data
            self.telemetry_client.track_trace("YES answer", properties, "INFO")
            return await step_context.end_dialog(booking_details)
        
        # If the BOT is NOT successful
        else:
            # Send an apology message to the user
            sorry_msg = "I'm sorry I couldn't help you"
            prompt_sorry_msg = MessageFactory.text(sorry_msg, sorry_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_sorry_msg)

            # Track NO data
            self.telemetry_client.track_trace("NO answer", properties, "ERROR")

        return await step_context.end_dialog()
