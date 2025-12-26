import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import FormatStrFormatter
import argparse


class SecurityAnalyzer:
    def __init__(self, jsonl_path: str, output_dir: str):
        self.df = pd.read_json(jsonl_path, lines=True)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.output_path = Path(output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.active_defenses = self._determine_active_defenses()

        self.colors = {
            'weak': '#ff7675', 'medium': '#fdcb6e', 'strong': '#55efc4',
            'Attempts': '#0984e3', 'Time': '#6c5ce7', 'Fail': '#00b894', 'Success': '#d63031'
        }
        sns.set_theme(style="whitegrid", font_scale=0.75)

    def _determine_active_defenses(self):
        if self.df.empty: return []
        row = self.df.iloc[0]
        layers = {
            'pepper': 'Pepper', 'account_lockout': 'Account Lockout',
            'rate_limit': 'Rate Limiting', 'captcha': 'Captcha', 'totp': 'TOTP Auth'
        }
        return [(k, v) for k, v in layers.items() if str(row.get(k, '')).lower() == 'true']

    def get_attack_metrics(self):
        results = []
        for user, group in self.df.groupby('username'):
            group = group.sort_values('timestamp')
            success = group[group['success'] == True]
            strength = group['password_score'].iloc[0] if 'password_score' in group.columns else "Unknown"

            if not success.empty:
                first = success.iloc[0]
                results.append({
                    'username': user, 'strength': strength,
                    'attempts': len(group[group['timestamp'] <= first['timestamp']]),
                    'time_sec': (first['timestamp'] - group.iloc[0]['timestamp']).total_seconds(),
                    'timestamp': first['timestamp'], 'success': True
                })
            else:
                results.append({
                    'username': user, 'strength': strength, 'attempts': len(group),
                    'time_sec': (group.iloc[-1]['timestamp'] - group.iloc[0]['timestamp']).total_seconds(),
                    'timestamp': group.iloc[-1]['timestamp'], 'success': False
                })
        return pd.DataFrame(results)

    def _create_summery_box(self, fig, pos):
        ax = fig.add_axes(pos)
        ax.axis('off')
        perf = self.df['latency_ms']
        attack_df = self.get_attack_metrics()
        breached = attack_df[attack_df['success'] == True]
        safe = attack_df[attack_df['success'] == False]

        total_attempts, total_users = len(self.df), self.df['username'].nunique()
        num_breached, num_protected = len(breached), len(safe)
        breached_pct = (num_breached / total_users * 100) if total_users > 0 else 0
        protected_pct = (num_protected / total_users * 100) if total_users > 0 else 0

        server_perf = (
            f"SERVER PERFORMANCE\n"
            f"• Latency (ms):   Avg: {perf.mean():<7.2f} | Med: {perf.median():<7.2f}\n"
            f"• CPU (ms):       Avg: {self.df['cpu_usage_ms'].mean():<7.4f} | Med: {self.df['cpu_usage_ms'].median():<7.4f}\n"
            f"• Memory (mb):    Avg: {self.df['memory_delta_mb'].mean():<7.4f} | Med: {self.df['memory_delta_mb'].median():<7.4f}\n"
        )
        attack_eff = (
            f"ATTACK EFFICIENCY & OUTCOME\n"
            f"• Total Login Attempts:      {total_attempts}\n"
            f"• Total Targeted Accounts:   {total_users}\n"
            f"• Accounts Breached:         {num_breached:<4} ({breached_pct:>5.1f}%)\n"
            f"• Accounts Protected:        {num_protected:<4} ({protected_pct:>5.1f}%)\n"
            f"• Avg Attempts / Breached:   {breached['attempts'].mean() if not breached.empty else 0:.1f}\n"
            f"• Avg Attempts / Protected:  {safe['attempts'].mean() if not safe.empty else 0:.1f}\n"
            f"• Avg Time to Breach:        {breached['time_sec'].mean() if not breached.empty else 0:.2f}s"
        )
        ax.text(0.05, 0.95, f"{server_perf}\n\n{attack_eff}", transform=ax.transAxes, family='monospace', fontsize=7,
                va='top', ha='left', linespacing=1.5,
                bbox=dict(facecolor='#f0f3ff', edgecolor='#74b9ff', boxstyle='round,pad=1', alpha=0.8))

    def _create_config_box(self, fig, pos, input_file):

        ax = fig.add_axes(pos)
        ax.axis('off')
        row = self.df.iloc[0]
        separator = "-" * 30
        config_lines = ["EXPERIMENT CONFIGURATION",
                        separator,
                        "• Group Seed: 509041496",
                        f"• Hash Type: {str(row.get('hash_type', 'N/A'))}"
                        f"\n\nProtections:"]

        for _, display_name in self.active_defenses:
            config_lines.append(f"• {display_name:<28}")
        if not self.active_defenses: config_lines.append("• No active defenses")

        ax.text(0.05, 0.95, "\n".join(config_lines), transform=ax.transAxes, family='monospace', fontsize=7, va='top',
                ha='left', linespacing=1.4,
                bbox=dict(facecolor='#f0f3ff', edgecolor='#74b9ff', boxstyle='round,pad=1', alpha=0.8))

    def _plot_success_pie_charts(self, fig, pos_base):
        attack_df = self.get_attack_metrics()
        categories = ['weak', 'medium', 'strong']
        for i, cat in enumerate(categories):
            ax_pos = [pos_base[0] + (i * 0.1), pos_base[1], 0.08, 0.08]
            ax = fig.add_axes(ax_pos)
            cat_data = attack_df[attack_df['strength'] == cat]
            if cat_data.empty:
                ax.text(0.5, 0.5, f'{cat.capitalize()}\nNo Data', ha='center', va='center', fontsize=6, color='gray')
                ax.axis('off');
                continue
            counts = cat_data['success'].value_counts().reindex([True, False], fill_value=0)
            ax.pie(counts, colors=[self.colors['Success'], self.colors['Fail']], startangle=90,
                   wedgeprops={'alpha': 0.6, 'edgecolor': 'white', 'linewidth': 1})
            ax.add_artist(plt.Circle((0, 0), 0.70, fc='white'))
            ax.text(0, 0, f'{int((counts[True] / len(cat_data)) * 100)}%', ha='center', va='center', fontsize=8,
                    fontweight='bold')
            ax.set_title(cat.capitalize(), fontsize=8, pad=5, fontweight='semibold')

        desc_y, legend_y = pos_base[1] - 0.005, pos_base[1] - 0.025
        fig.text(pos_base[0] + 0.14, desc_y, 'Percentage of accounts compromised per password score', fontsize=7,
                 color='gray',
                 ha='center', style='italic')
        for label, color, offset in [('Breached', 'Success', 0.06), ('Protected', 'Fail', 0.16)]:
            fig.patches.append(
                plt.Rectangle((pos_base[0] + offset, legend_y), 0.01, 0.01, facecolor=self.colors[color], alpha=0.7,
                              transform=fig.transFigure))
            fig.text(pos_base[0] + offset + 0.015, legend_y + 0.002, label, fontsize=7, va='bottom')

    def _plot_avg_login_attempts(self, ax):
        attack_df = self.get_attack_metrics()
        if attack_df.empty: return
        order = ['weak', 'medium', 'strong']
        summary = attack_df.groupby(['strength', 'success'])['attempts'].mean().unstack(fill_value=0).reindex(
            order).fillna(
            0)
        for col in [True, False]:
            if col not in summary.columns: summary[col] = 0
        x, width = range(len(order)), 0.4
        r1 = ax.bar([p - width / 2 for p in x], summary[True], width, label='Avg. attempts until breached',
                    color=self.colors['Success'], edgecolor='black', lw=0.8)
        r2 = ax.bar([p + width / 2 for p in x], summary[False], width, label='Avg. attempts per non breached account',
                    color=self.colors['Fail'], alpha=0.7, edgecolor='black', lw=0.8)
        ax.set_title('Average Login Attempts', fontweight='bold', pad=18)
        ax.set_ylabel('Number of Attempts (avg)', fontweight='bold')
        ax.set_xticks(x);
        ax.set_xticklabels(['Weak', 'Medium', 'Strong'])
        for r in [r1, r2]:
            for b in r:
                h = b.get_height()
                if h > 0: ax.annotate(f'{h:.1f}', xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                                      textcoords="offset points", ha='center', va='bottom', fontsize=7,
                                      fontweight='bold')
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, fontsize=8, frameon=True)
        sns.despine(ax=ax)


    def _plot_blocking_factor(self, ax):
        failed = self.df[self.df['success'] == False]
        if failed.empty:
            ax.text(0.5, 0.5, 'No Failures Recorded', ha='center', va='center')
            ax.axis('off')
            return

        failure_counts = failed['failure_reason'].value_counts()
        colors = sns.color_palette("husl", len(failure_counts))

        wedges, texts, autotexts = ax.pie(
            failure_counts,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 0.8, 'alpha': 0.9}
        )

        plt.setp(autotexts, size=7, fontweight="bold", color="black")

        ax.legend(
            wedges,
            failure_counts.index,
            title="Failure Reasons",
            loc="center left",
            bbox_to_anchor=(0.95, 0, 0.5, 1),
            fontsize=8,
            frameon=True
        )
        ax.set_title('Blocking Factors Distribution', fontweight='bold', pad=15)
        ax.axis('equal')


    def _plot_requests_over_time(self, ax):

        start_time_experiment = self.df['timestamp'].min()
        df_copy = self.df.copy()
        df_copy['relative_time'] = (df_copy['timestamp'] - start_time_experiment).dt.total_seconds()
        df_sorted = df_copy.sort_values('relative_time')

        intensity = df_sorted.copy()
        intensity['rel_time_rounded'] = intensity['relative_time'].round()
        intensity = intensity.groupby('rel_time_rounded').size().reset_index()
        intensity.columns = ['rel_time', 'count']
        intensity['rel_time'] = intensity['rel_time'].astype(float)
        ax.plot(intensity['rel_time'], intensity['count'], color='navy', alpha=0.75, lw=1, label='Requests/sec')
        ax.fill_between(intensity['rel_time'], intensity['count'], alpha=0.25, color='navy')

        breaches = df_sorted[df_sorted['success'] == True].copy()
        breach_details = []

        if not breaches.empty:
            user_start_times = df_sorted.groupby('username')['relative_time'].min()

            breaches = pd.merge_asof(
                breaches.sort_values('relative_time'),
                intensity.sort_values('rel_time'),
                left_on='relative_time',
                right_on='rel_time',
                direction='nearest'
            )

            for s in ['weak', 'medium', 'strong']:
                sub = breaches[breaches['password_score'] == s]
                if not sub.empty:
                    ax.scatter(sub['relative_time'], sub['count'], color=self.colors[s], marker='o',
                               s=60, alpha=0.9, label=f'Breach {s}', edgecolor='black', lw=0.8, zorder=5)

                    breach_details.append('\n' + s.upper())
                    for _, row in sub.iterrows():
                        duration = row['relative_time'] - user_start_times[row['username']]
                        line = f"{row['username']:-<8} {duration:.3f}s"
                        breach_details.append(line)

        ax.set_title('Requests over Time', fontweight='bold', pad=15)
        ax.set_xlabel('Seconds from Start')
        ax.set_ylabel('Requests / second')

        h, l = ax.get_legend_handles_labels()
        d = dict(zip(l, h))
        ax.legend(d.values(), d.keys(), fontsize=8, loc='upper center',
                  bbox_to_anchor=(0.5, -0.15), ncol=len(d), frameon=True)

        if breach_details:
            internal_text = "Time to Breach:\n" + "\n".join(breach_details)
            ax.text(0.98, 0.05, internal_text, transform=ax.transAxes,
                    fontsize=7, va='bottom', ha='right', multialignment='left', family='monospace',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7, edgecolor='gray'),
                    zorder=10)

        ax.xaxis.set_major_formatter(FormatStrFormatter('%ds'))



    def _add_empty_box_border(self, ax):
        ax.set_xticks([]);
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True);
            spine.set_color('#dfe6e9');
            spine.set_linewidth(1);
            spine.set_linestyle('--')

    def save_single_page_report(self, input_file):
        pdf_path = self.output_path / "analysis_report.pdf"
        fig = plt.figure(figsize=(10, 15))

        # header
        fig.suptitle(f"\nSecurity Analysis Research Report",
                     fontsize=16, fontweight='bold', y=0.95, color='#2d3436', ha='center')

        # upper graphs
        self._create_summery_box(fig, [0.09, 0.80, 0.25, 0.08])
        self._plot_success_pie_charts(fig, [0.4, 0.80])
        self._create_config_box(fig, [0.7, 0.80, 0.25, 0.08], input_file)

        # -lower graph
        gs = fig.add_gridspec(2, 2, left=0.1, right=0.9, bottom=0.08, top=0.68, hspace=0.5, wspace=0.35)
        self._plot_avg_login_attempts(fig.add_subplot(gs[1, 1]))
        self._add_empty_box_border(fig.add_subplot(gs[0, 1]))
        self._plot_requests_over_time(fig.add_subplot(gs[1, 0]))
        self._plot_blocking_factor(fig.add_subplot(gs[0, 0]))

        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

        print(f"✓ Final polished report generated: {pdf_path.resolve()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    input_dir = input_path.parent

    analyzer = SecurityAnalyzer(str(input_path), str(input_dir))
    analyzer.save_single_page_report(str(input_path))


if __name__ == "__main__":
    main()
