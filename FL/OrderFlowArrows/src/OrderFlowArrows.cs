// -------------------------------------------------------------
// OrderFlowArrows.cs  —  ATAS custom indicator
// -------------------------------------------------------------
// Plots an Up/Down arrow per bar based on Bid-Ask delta + bar direction.
//
// Bullish: (BidVol - AskVol) >= MinDeltaThreshold AND Close >= Open
// Bearish: (BidVol - AskVol) <= -MinDeltaThreshold AND Close < Open
//
// Arrows are positioned at High + offset (bull) and Low - offset (bear).
// Includes optional sound alert fired when a *new* arrow appears.
// -------------------------------------------------------------

using System;
using System.ComponentModel;
using System.Drawing;

// NOTE: Adjust these namespaces to match your ATAS SDK version.
using ATAS.Indicators;
using ATAS.Indicators.Drawing;
using ATAS.IndicatorsBase;       // common in many versions
using ATAS.Platform;             // bar data access
using ATAS.Platform.Controls;    // colors, UI attributes
using ATAS.Platform.Indicators;  // Indicator base
using ATAS.Series;               // ValueDataSeries etc.

namespace CustomIndicators
{
    [DisplayName("Order Flow Arrows (Tick)")]
    [Description("Plots arrows using Bid-Ask delta and bar direction.")]
    public class OrderFlowArrows : Indicator
    {
        // -------------------------
        // Inputs (editable in menu)
        // -------------------------

        [Category("Parameters")]
        [DisplayName("Min Delta Threshold")]
        [Description("Absolute delta required to print an arrow.")]
        public int MinDeltaThreshold { get; set; } = 100;

        [Category("Parameters")]
        [DisplayName("Arrow Offset (ticks)")]
        [Description("Offset above High / below Low for arrow placement.")]
        public int ArrowOffsetTicks { get; set; } = 2;

        [Category("Style")]
        [DisplayName("Bullish Color")]
        public Color BullishColor { get; set; } = Color.LimeGreen;

        [Category("Style")]
        [DisplayName("Bearish Color")]
        public Color BearishColor { get; set; } = Color.OrangeRed;

        [Category("Alerts")]
        [DisplayName("Enable Sound Alert")]
        public bool EnableSound { get; set; } = false;

        [Category("Alerts")]
        [DisplayName("Sound File (optional)")]
        [Description("Leave blank to use the platform default sound.")]
        public string SoundFile { get; set; } = string.Empty;

        // -------------------------
        // Plot series
        // -------------------------

        private readonly ValueDataSeries _bullArrows = new("Bullish")
        {
            // ATAS commonly supports arrow visual types via the series setup.
            // If your SDK uses VisualMode/Type differently, adjust here:
            VisualType = VisualMode.UpArrow,
            Color = Color.LimeGreen,
            ShowZeroValues = false
        };

        private readonly ValueDataSeries _bearArrows = new("Bearish")
        {
            VisualType = VisualMode.DownArrow,
            Color = Color.OrangeRed,
            ShowZeroValues = false
        };

        // Track last alerted bar index so we don't double-play sounds
        private int _lastAlertedBar = -1;

        public OrderFlowArrows()
        {
            // Register the series so ATAS renders them on the price panel
            DataSeries.Add(_bullArrows);
            DataSeries.Add(_bearArrows);

            // Apply default colors from inputs
            _bullArrows.Color = BullishColor;
            _bearArrows.Color = BearishColor;

            // Indicator draws on the main chart by default
            DenyToChangePanel = true;
        }

        // If your SDK supports property change notification hooks, update live:
        protected override void OnPropertiesChanged()
        {
            _bullArrows.Color = BullishColor;
            _bearArrows.Color = BearishColor;
        }

        // -------------------------------------------------------------
        // Core calculation: called for each bar (updates on each tick
        // for the current bar; runs over all bars for historical data).
        // -------------------------------------------------------------
        protected override void OnCalculate(int bar)
        {
            if (bar < 0 || bar >= CurrentBar)
                return;

            // 1) Read OHLC for the bar
            var open  = GetPrice(PriceType.Open, bar);
            var high  = GetPrice(PriceType.High, bar);
            var low   = GetPrice(PriceType.Low, bar);
            var close = GetPrice(PriceType.Close, bar);

            // 2) Get per-bar Bid/Ask volumes
            // NOTE: Replace with your SDK’s exact accessors if names differ:
            long bidVol = GetBarBidVolume(bar);
            long askVol = GetBarAskVolume(bar);

            // 3) Compute delta and bar direction
            long delta = bidVol - askVol;
            bool bullBar = close >= open;
            bool bearBar = close < open;

            // 4) Decide if we print an arrow
            bool printBull = bullBar && delta >= MinDeltaThreshold;
            bool printBear = bearBar && delta <= -MinDeltaThreshold;

            // Clear previous values for this bar (avoid overlaps)
            _bullArrows[bar] = 0m;
            _bearArrows[bar] = 0m;

            if (printBull)
            {
                decimal offset = TicksToPrice(ArrowOffsetTicks);
                _bullArrows[bar] = high + offset;

                TryAlert(bar);
            }
            else if (printBear)
            {
                decimal offset = TicksToPrice(ArrowOffsetTicks);
                _bearArrows[bar] = low - offset;

                TryAlert(bar);
            }
        }

        // -------------------------
        // Helpers (SDK adaptation)
        // -------------------------

        private void TryAlert(int bar)
        {
            if (!EnableSound)
                return;

            // Avoid multiple alerts on repeated recalcs of the same bar
            if (bar == _lastAlertedBar)
                return;

            _lastAlertedBar = bar;

            // Play sound (use default if SoundFile empty)
            try
            {
                if (!string.IsNullOrWhiteSpace(SoundFile))
                    Alerts.PlaySound(SoundFile);
                else
                    Alerts.PlayDefaultSound();
            }
            catch
            {
                // Non-fatal: ignore sound failures so the indicator still works
            }
        }

        private decimal TicksToPrice(int ticks)
        {
            // Convert N ticks to price units via instrument tick size
            var ts = InstrumentInfo.TickSize;   // adjust to your SDK symbol info
            return (decimal)ticks * (decimal)ts;
        }

        private decimal GetPrice(PriceType type, int bar)
        {
            // Common ATAS accessors; adjust if your SDK differs
            return type switch
            {
                PriceType.Open  => Open[bar],
                PriceType.High  => High[bar],
                PriceType.Low   => Low[bar],
                PriceType.Close => Close[bar],
                _ => Close[bar]
            };
        }

        private long GetBarBidVolume(int bar)
        {
            // ATAS usually exposes per-bar Bid/Ask volumes historically and live.
            // Replace with the exact property if different in your SDK version:
            return (long)Bid[bar];
        }

        private long GetBarAskVolume(int bar)
        {
            // Replace with the exact accessor as needed:
            return (long)Ask[bar];
        }
    }

    // Small enum alias to keep GetPrice tidy; adapt if your SDK already defines it.
    internal enum PriceType { Open, High, Low, Close }
}
