import plotly.graph_objects as go

class MetricsPlotter:
    def __init__(self, data, title='Metrics Evaluation', width=800, output_file='evaluation_plot.html'):
        self.data = data
        self.title = title
        self.width = width
        self.margin = dict(l=100,r=100, t=100, b=100, pad=10)
        self.output_file = output_file
    
    def compute_averages(self):
        total_faithfulness = 0.0
        total_answer_relevancy = 0.0
        total_context_precision = 0.0
        total_context_recall = 0.0
        total_answer_correctness = 0.0
        total_answer_similarity = 0.0

        num_results = len(self.data)

        for res in self.data:
            total_faithfulness += res['faithfulness']
            total_answer_relevancy += res['answer_relevancy']
            total_context_precision += res['context_precision']
            total_context_recall += res['context_recall']
            total_answer_correctness += res['answer_correctness']
            total_answer_similarity += res['answer_similarity']

        average_faithfulness = total_faithfulness / num_results if num_results > 0 else 0.0
        average_answer_relevancy = total_answer_relevancy / num_results if num_results > 0 else 0.0
        average_context_precision = total_context_precision / num_results if num_results > 0 else 0.0
        average_context_recall = total_context_recall / num_results if num_results > 0 else 0.0
        average_answer_correctness = total_answer_correctness / num_results if num_results > 0 else 0.0
        average_answer_similarity = total_answer_similarity / num_results if num_results > 0 else 0.0

        self.averages = {
            'context_precision': average_context_precision,
            'faithfulness': average_faithfulness,
            'answer_relevancy': average_answer_relevancy,
            'context_recall': average_context_recall,
            'answer_correctness': average_answer_correctness,
            'answer_similarity': average_answer_similarity
        }

    def plot_metrics(self):
        if isinstance(self.data, list) and len(self.data) > 1:
            self.compute_averages()
            plot_data = self.averages
        else:
            plot_data = self.data if isinstance(self.data, dict) else self.data[0]

        r_values = list(plot_data.values())
        theta_values = list(plot_data.keys())
        r_values.append(r_values[0])
        theta_values.append(theta_values[0])
        
        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=r_values,
            theta=theta_values,
            fill='toself',
            name='Metrics Trace'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title=dict(
                text=self.title,
                x=0.5,
                y=0.95,
                xanchor='center',
                yanchor='top',
            ),
            width=self.width,
            margin=dict(t=100, b=50, l=50, r=50)  # Adjust these values as needed
        )

        fig.write_html(self.output_file)

