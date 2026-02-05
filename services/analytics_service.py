"""
GeminiCRM Pro - Advanced Analytics & Reporting
Comprehensive analytics, reporting, and business intelligence
"""
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# ==================== ANALYTICS ENGINE ====================

class AnalyticsEngine:
    """Advanced analytics and reporting"""
    
    @staticmethod
    def calculate_lead_metrics(leads):
        """Calculate comprehensive lead metrics"""
        if not leads:
            return {}
        
        scores = [l.get('score', 0) for l in leads]
        sources = [l.get('source') for l in leads]
        statuses = [l.get('status') for l in leads]
        
        return {
            'total_leads': len(leads),
            'avg_score': round(statistics.mean(scores), 1) if scores else 0,
            'median_score': round(statistics.median(scores), 1) if scores else 0,
            'high_quality_leads': len([l for l in leads if l.get('score', 0) >= 80]),
            'by_source': dict(sorted(
                [(s, len([l for l in leads if l.get('source') == s])) for s in set(sources) if s],
                key=lambda x: x[1],
                reverse=True
            )),
            'by_status': dict([(s, len([l for l in leads if l.get('status') == s])) for s in set(statuses) if s]),
            'conversion_rate': f"{(len([l for l in leads if l.get('status') == 'won']) / len(leads) * 100):.1f}%" if leads else "0%"
        }
    
    @staticmethod
    def calculate_deal_metrics(deals):
        """Calculate comprehensive deal metrics"""
        if not deals:
            return {}
        
        values = [d.get('value', 0) for d in deals]
        stages = [d.get('stage') for d in deals]
        probabilities = [d.get('probability', 0) for d in deals]
        
        total_value = sum(values)
        weighted_value = sum([d.get('value', 0) * (d.get('probability', 0) / 100) for d in deals])
        
        won_deals = [d for d in deals if d.get('stage') == 'closed_won']
        lost_deals = [d for d in deals if d.get('stage') == 'closed_lost']
        
        return {
            'total_deals': len(deals),
            'total_pipeline_value': total_value,
            'weighted_pipeline_value': round(weighted_value),
            'avg_deal_value': round(total_value / len(deals), 2) if deals else 0,
            'total_won_value': sum([d.get('value', 0) for d in won_deals]),
            'total_lost_value': sum([d.get('value', 0) for d in lost_deals]),
            'won_deals_count': len(won_deals),
            'lost_deals_count': len(lost_deals),
            'win_rate': f"{(len(won_deals) / len(deals) * 100):.1f}%" if deals else "0%",
            'avg_probability': round(statistics.mean(probabilities), 1) if probabilities else 0,
            'by_stage': dict([(s, len([d for d in deals if d.get('stage') == s])) for s in set(stages) if s])
        }
    
    @staticmethod
    def calculate_sales_metrics(contacts, leads, deals):
        """Calculate overall sales metrics"""
        return {
            'total_contacts': len(contacts),
            'total_leads': len(leads),
            'total_deals': len(deals),
            'lead_to_deal_ratio': f"{(len(deals) / len(leads) * 100):.1f}%" if leads else "0%",
            'contact_to_lead_ratio': f"{(len(leads) / len(contacts) * 100):.1f}%" if contacts else "0%"
        }
    
    @staticmethod
    def get_forecast(deals, period_days=30):
        """Get sales forecast for next N days"""
        today = datetime.now()
        forecast_date = today + timedelta(days=period_days)
        
        forecasted_deals = [
            d for d in deals 
            if d.get('stage') != 'closed_won' and d.get('stage') != 'closed_lost'
        ]
        
        total_forecast = 0
        for deal in forecasted_deals:
            value = deal.get('value', 0)
            probability = deal.get('probability', 0) / 100
            total_forecast += value * probability
        
        return {
            'period_days': period_days,
            'forecast_value': round(total_forecast),
            'deals_in_forecast': len(forecasted_deals),
            'confidence': 'Medium'
        }
    
    @staticmethod
    def get_pipeline_analysis(deals):
        """Detailed pipeline analysis by stage"""
        stages = {}
        for deal in deals:
            stage = deal.get('stage', 'unknown')
            if stage not in stages:
                stages[stage] = {
                    'count': 0,
                    'value': 0,
                    'avg_value': 0,
                    'avg_probability': 0,
                    'deals': []
                }
            
            stages[stage]['count'] += 1
            stages[stage]['value'] += deal.get('value', 0)
            stages[stage]['deals'].append(deal)
        
        for stage, data in stages.items():
            if data['count'] > 0:
                data['avg_value'] = round(data['value'] / data['count'], 2)
                probabilities = [d.get('probability', 0) for d in data['deals']]
                data['avg_probability'] = round(statistics.mean(probabilities), 1)
            data.pop('deals')
        
        return stages
    
    @staticmethod
    def get_team_performance(users, deals_by_user):
        """Analyze team member performance"""
        performance = {}
        
        for user in users:
            user_id = user.get('id')
            user_deals = deals_by_user.get(user_id, [])
            
            if user_deals:
                won = len([d for d in user_deals if d.get('stage') == 'closed_won'])
                total_value = sum([d.get('value', 0) for d in user_deals])
                
                performance[user_id] = {
                    'name': user.get('full_name', user.get('username')),
                    'deals_count': len(user_deals),
                    'won_deals': won,
                    'win_rate': f"{(won / len(user_deals) * 100):.1f}%" if user_deals else "0%",
                    'total_value': total_value,
                    'avg_deal_value': round(total_value / len(user_deals), 2) if user_deals else 0
                }
        
        return performance

# ==================== REPORT GENERATION ====================

class ReportGenerator:
    """Generate various reports"""
    
    @staticmethod
    def generate_executive_summary(contacts, leads, deals, tasks):
        """Generate executive summary report"""
        analytics = AnalyticsEngine()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'title': 'Executive Summary',
            'metrics': {
                'leads': analytics.calculate_lead_metrics(leads),
                'deals': analytics.calculate_deal_metrics(deals),
                'sales': analytics.calculate_sales_metrics(contacts, leads, deals),
                'forecast': analytics.get_forecast(deals, 30)
            },
            'pipeline': analytics.get_pipeline_analysis(deals)
        }
    
    @staticmethod
    def generate_lead_report(leads):
        """Generate detailed lead report"""
        analytics = AnalyticsEngine()
        
        by_source = defaultdict(list)
        by_status = defaultdict(list)
        
        for lead in leads:
            by_source[lead.get('source')].append(lead)
            by_status[lead.get('status')].append(lead)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'title': 'Lead Report',
            'summary': analytics.calculate_lead_metrics(leads),
            'by_source': dict([(k, len(v)) for k, v in by_source.items()]),
            'by_status': dict([(k, len(v)) for k, v in by_status.items()])
        }
    
    @staticmethod
    def generate_deal_report(deals):
        """Generate detailed deal report"""
        analytics = AnalyticsEngine()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'title': 'Deal Report',
            'summary': analytics.calculate_deal_metrics(deals),
            'pipeline': analytics.get_pipeline_analysis(deals)
        }
    
    @staticmethod
    def generate_sales_forecast(deals, period_days=90):
        """Generate sales forecast report"""
        analytics = AnalyticsEngine()
        
        daily_forecast = {}
        today = datetime.now().date()
        
        for i in range(period_days):
            date = today + timedelta(days=i)
            date_str = date.isoformat()
            daily_forecast[date_str] = round(sum([
                d.get('value', 0) * (d.get('probability', 0) / 100)
                for d in deals
                if d.get('stage') not in ['closed_won', 'closed_lost']
            ]))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'title': f'{period_days}-Day Sales Forecast',
            'period_days': period_days,
            'daily_forecast': daily_forecast,
            'summary': analytics.get_forecast(deals, period_days)
        }

# ==================== EXPORT UTILITIES ====================

class ExportManager:
    """Handle data export in various formats"""
    
    @staticmethod
    def export_to_csv(data, columns):
        """Export data to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(data):
        """Export data to JSON format"""
        import json
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def export_to_excel(data, filename='export.xlsx'):
        """Export data to Excel format"""
        try:
            import openpyxl
            from openpyxl.utils.dataframe import dataframe_to_rows
            import pandas as pd
            
            df = pd.DataFrame(data)
            wb = openpyxl.Workbook()
            ws = wb.active
            
            for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
                for c_idx, value in enumerate(row, 1):
                    ws.cell(row=r_idx, column=c_idx, value=value)
            
            wb.save(filename)
            return filename
        except ImportError:
            return None

# ==================== IMPORT UTILITIES ====================

class ImportManager:
    """Handle data import from various formats"""
    
    @staticmethod
    def import_from_csv(file_content):
        """Import data from CSV"""
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(file_content))
        return list(reader)
    
    @staticmethod
    def import_from_json(file_content):
        """Import data from JSON"""
        import json
        return json.loads(file_content)
    
    @staticmethod
    def validate_import_data(data, schema):
        """Validate imported data against schema"""
        errors = []
        
        for i, row in enumerate(data):
            for field, field_type in schema.items():
                if field not in row:
                    errors.append(f"Row {i}: Missing field '{field}'")
                elif field_type == 'number':
                    try:
                        float(row[field])
                    except ValueError:
                        errors.append(f"Row {i}: '{field}' is not a valid number")
        
        return errors if errors else None
