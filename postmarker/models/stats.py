from .base import ModelManager


class StatsManager(ModelManager):
    name = "stats"

    def overview(self, tag=None, fromdate=None, todate=None):
        """Gets a brief overview of statistics for all of your outbound email."""
        return self.call("GET", "/stats/outbound", tag=tag, fromdate=fromdate, todate=todate)

    def sends(self, tag=None, fromdate=None, todate=None):
        """Gets a total count of emails you’ve sent out."""
        return self.call("GET", "/stats/outbound/sends", tag=tag, fromdate=fromdate, todate=todate)

    def bounces(self, tag=None, fromdate=None, todate=None):
        """Gets total counts of emails you’ve sent out that have been returned as bounced."""
        return self.call("GET", "/stats/outbound/bounces", tag=tag, fromdate=fromdate, todate=todate)

    def spam(self, tag=None, fromdate=None, todate=None):
        """Gets a total count of recipients who have marked your email as spam."""
        return self.call("GET", "/stats/outbound/spam", tag=tag, fromdate=fromdate, todate=todate)

    def tracked(self, tag=None, fromdate=None, todate=None):
        """Gets a total count of emails you’ve sent with open tracking or link tracking enabled."""
        return self.call("GET", "/stats/outbound/tracked", tag=tag, fromdate=fromdate, todate=todate)

    def opens(self, tag=None, fromdate=None, todate=None):
        """Gets total counts of recipients who opened your emails.

        This is only recorded when open tracking is enabled for that email.
        """
        return self.call("GET", "/stats/outbound/opens", tag=tag, fromdate=fromdate, todate=todate)

    def opens_platforms(self, tag=None, fromdate=None, todate=None):
        """Gets an overview of the platforms used to open your emails.

        This is only recorded when open tracking is enabled for that email.
        """
        return self.call(
            "GET",
            "/stats/outbound/opens/platforms",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )

    def emailclients(self, tag=None, fromdate=None, todate=None):
        """Gets an overview of the email clients used to open your emails.

        This is only recorded when open tracking is enabled for that email.
        """
        return self.call(
            "GET",
            "/stats/outbound/opens/emailclients",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )

    def readtimes(self, tag=None, fromdate=None, todate=None):
        """Gets the length of time that recipients read emails along with counts for each time.

        This is only recorded when open tracking is enabled for that email.
        Read time tracking stops at 20 seconds, so any read times above that will appear in the 20s+ field.
        """
        return self.call(
            "GET",
            "/stats/outbound/opens/readtimes",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )

    def clicks(self, tag=None, fromdate=None, todate=None):
        """Gets total counts of unique links that were clicked."""
        return self.call("GET", "/stats/outbound/clicks", tag=tag, fromdate=fromdate, todate=todate)

    def browserfamilies(self, tag=None, fromdate=None, todate=None):
        """Gets an overview of the browsers used to open links in your emails.

        This is only recorded when Link Tracking is enabled for that email.
        """
        return self.call(
            "GET",
            "/stats/outbound/clicks/browserfamilies",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )

    def clicks_platforms(self, tag=None, fromdate=None, todate=None):
        """Gets an overview of the browser platforms used to open your emails.

        This is only recorded when Link Tracking is enabled for that email.
        """
        return self.call(
            "GET",
            "/stats/outbound/clicks/platforms",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )

    def location(self, tag=None, fromdate=None, todate=None):
        """Gets an overview of which part of the email links were clicked from (HTML or Text).

        This is only recorded when Link Tracking is enabled for that email.
        """
        return self.call(
            "GET",
            "/stats/outbound/clicks/location",
            tag=tag,
            fromdate=fromdate,
            todate=todate,
        )
