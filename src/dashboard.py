#!/usr/bin/env python3
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

class MetricsDashboard:
    def __init__(self):
        self.init_metrics_db()
    
    def init_metrics_db(self):
        """Initialize metrics database"""
        self.conn = sqlite3.connect("metrics.db", check_same_thread=False)
        
        # Chat metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_metrics (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                cost REAL,
                latency_ms INTEGER
            )
        """)
        
        # RAG metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rag_metrics (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                query TEXT,
                retrieval_time_ms REAL,
                total_time_ms REAL,
                accuracy REAL
            )
        """)
        
        # Agent metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                task_type TEXT,
                success BOOLEAN,
                attempts INTEGER,
                total_time_ms REAL
            )
        """)
        
        self.conn.commit()
        
        # Insert sample data if tables are empty
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data for demonstration"""
        
        # Check if data exists
        cursor = self.conn.execute("SELECT COUNT(*) FROM chat_metrics")
        if cursor.fetchone()[0] > 0:
            return
        
        # Generate sample chat metrics
        base_time = datetime.now().timestamp() - 86400  # 24 hours ago
        
        for i in range(50):
            timestamp = base_time + (i * 1800)  # Every 30 minutes
            prompt_tokens = np.random.randint(10, 100)
            completion_tokens = np.random.randint(20, 200)
            cost = (prompt_tokens * 5 + completion_tokens * 15) / 1_000_000
            latency = np.random.randint(200, 2000)
            
            self.conn.execute("""
                INSERT INTO chat_metrics (timestamp, prompt_tokens, completion_tokens, cost, latency_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, prompt_tokens, completion_tokens, cost, latency))
        
        # Generate sample RAG metrics
        for i in range(30):
            timestamp = base_time + (i * 2400)
            retrieval_time = np.random.uniform(50, 300)
            total_time = retrieval_time + np.random.uniform(500, 2000)
            accuracy = np.random.uniform(0.6, 0.95)
            
            self.conn.execute("""
                INSERT INTO rag_metrics (timestamp, query, retrieval_time_ms, total_time_ms, accuracy)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, f"Sample query {i}", retrieval_time, total_time, accuracy))
        
        # Generate sample agent metrics
        task_types = ["trip_planning", "code_generation", "data_analysis"]
        for i in range(25):
            timestamp = base_time + (i * 3600)
            task_type = np.random.choice(task_types)
            success = np.random.choice([True, False], p=[0.8, 0.2])
            attempts = np.random.randint(1, 4)
            total_time = np.random.uniform(5000, 30000)
            
            self.conn.execute("""
                INSERT INTO agent_metrics (timestamp, task_type, success, attempts, total_time_ms)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, task_type, success, attempts, total_time))
        
        self.conn.commit()
    
    def get_chat_metrics(self):
        """Get chat metrics from database"""
        query = """
            SELECT timestamp, prompt_tokens, completion_tokens, cost, latency_ms
            FROM chat_metrics
            ORDER BY timestamp DESC
            LIMIT 100
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_rag_metrics(self):
        """Get RAG metrics from database"""
        query = """
            SELECT timestamp, retrieval_time_ms, total_time_ms, accuracy
            FROM rag_metrics
            ORDER BY timestamp DESC
            LIMIT 100
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_agent_metrics(self):
        """Get agent metrics from database"""
        query = """
            SELECT timestamp, task_type, success, attempts, total_time_ms
            FROM agent_metrics
            ORDER BY timestamp DESC
            LIMIT 100
        """
        df = pd.read_sql_query(query, self.conn)
        if not df.empty:
            # Convert success column to boolean
            df['success'] = df['success'].astype(bool)
        return df

def main():
    st.set_page_config(
        page_title="AI Platform Dashboard",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("AI Platform Assessment Dashboard")
    st.markdown("Real-time metrics for chat, RAG, and agent systems")
    
    dashboard = MetricsDashboard()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Overview",
        "Chat Metrics",
        "RAG Performance",
        "Agent Analytics"
    ])
    
    if page == "Overview":
        st.header("System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Get latest metrics
        chat_df = dashboard.get_chat_metrics()
        rag_df = dashboard.get_rag_metrics()
        agent_df = dashboard.get_agent_metrics()
        
        with col1:
            avg_latency = chat_df['latency_ms'].mean() if not chat_df.empty else 0
            st.metric("Avg Chat Latency", f"{avg_latency:.0f}ms")
        
        with col2:
            total_cost = chat_df['cost'].sum() if not chat_df.empty else 0
            st.metric("Total Cost (24h)", f"${total_cost:.4f}")
        
        with col3:
            avg_retrieval = rag_df['retrieval_time_ms'].mean() if not rag_df.empty else 0
            st.metric("Avg Retrieval Time", f"{avg_retrieval:.0f}ms")
        
        with col4:
            success_rate = agent_df['success'].astype(bool).mean() * 100 if not agent_df.empty else 0
            st.metric("Agent Success Rate", f"{success_rate:.1f}%")
        
        # Recent activity
        st.subheader("Recent Activity")
        
        if not chat_df.empty:
            chat_df['datetime'] = pd.to_datetime(chat_df['timestamp'], unit='s')
            recent_chat = chat_df.head(5)[['datetime', 'prompt_tokens', 'completion_tokens', 'latency_ms']]
            st.dataframe(recent_chat, use_container_width=True)
    
    elif page == "Chat Metrics":
        st.header("Chat System Metrics")
        
        chat_df = dashboard.get_chat_metrics()
        
        if not chat_df.empty:
            chat_df['datetime'] = pd.to_datetime(chat_df['timestamp'], unit='s')
            
            # Latency over time
            fig_latency = px.line(
                chat_df, x='datetime', y='latency_ms',
                title='Chat Latency Over Time',
                labels={'latency_ms': 'Latency (ms)', 'datetime': 'Time'}
            )
            st.plotly_chart(fig_latency, use_container_width=True)
            
            # Cost over time
            fig_cost = px.line(
                chat_df, x='datetime', y='cost',
                title='Cost Over Time',
                labels={'cost': 'Cost (USD)', 'datetime': 'Time'}
            )
            st.plotly_chart(fig_cost, use_container_width=True)
            
            # Token distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fig_tokens = px.histogram(
                    chat_df, x='prompt_tokens',
                    title='Prompt Tokens Distribution',
                    nbins=20
                )
                st.plotly_chart(fig_tokens, use_container_width=True)
            
            with col2:
                fig_completion = px.histogram(
                    chat_df, x='completion_tokens',
                    title='Completion Tokens Distribution',
                    nbins=20
                )
                st.plotly_chart(fig_completion, use_container_width=True)
    
    elif page == "RAG Performance":
        st.header("RAG System Performance")
        
        rag_df = dashboard.get_rag_metrics()
        
        if not rag_df.empty:
            rag_df['datetime'] = pd.to_datetime(rag_df['timestamp'], unit='s')
            
            # Retrieval time vs accuracy
            fig_scatter = px.scatter(
                rag_df, x='retrieval_time_ms', y='accuracy',
                title='Retrieval Time vs Accuracy',
                labels={'retrieval_time_ms': 'Retrieval Time (ms)', 'accuracy': 'Accuracy'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Accuracy over time
            fig_accuracy = px.line(
                rag_df, x='datetime', y='accuracy',
                title='Retrieval Accuracy Over Time',
                labels={'accuracy': 'Accuracy', 'datetime': 'Time'}
            )
            st.plotly_chart(fig_accuracy, use_container_width=True)
            
            # Performance metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Accuracy", f"{rag_df['accuracy'].mean():.2%}")
                st.metric("Median Retrieval Time", f"{rag_df['retrieval_time_ms'].median():.0f}ms")
            
            with col2:
                st.metric("95th Percentile Retrieval", f"{rag_df['retrieval_time_ms'].quantile(0.95):.0f}ms")
                st.metric("Total Queries", len(rag_df))
    
    elif page == "Agent Analytics":
        st.header("Agent Performance Analytics")
        
        agent_df = dashboard.get_agent_metrics()
        
        if not agent_df.empty:
            agent_df['datetime'] = pd.to_datetime(agent_df['timestamp'], unit='s')
            
            # Success rate by task type
            success_by_task = agent_df.groupby('task_type')['success'].mean().reset_index()
            fig_success = px.bar(
                success_by_task, x='task_type', y='success',
                title='Success Rate by Task Type',
                labels={'success': 'Success Rate', 'task_type': 'Task Type'}
            )
            fig_success.update_layout(yaxis_tickformat='.0%')
            st.plotly_chart(fig_success, use_container_width=True)
            
            # Attempts distribution
            fig_attempts = px.histogram(
                agent_df, x='attempts', color='success',
                title='Number of Attempts Distribution',
                nbins=5
            )
            st.plotly_chart(fig_attempts, use_container_width=True)
            
            # Task completion time
            fig_time = px.box(
                agent_df, x='task_type', y='total_time_ms',
                title='Task Completion Time by Type',
                labels={'total_time_ms': 'Time (ms)', 'task_type': 'Task Type'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Success Rate", f"{agent_df['success'].mean():.1%}")
            
            with col2:
                st.metric("Average Attempts", f"{agent_df['attempts'].mean():.1f}")
            
            with col3:
                st.metric("Average Completion Time", f"{agent_df['total_time_ms'].mean()/1000:.1f}s")
    
    # Auto-refresh option
    st.sidebar.markdown("---")
    if st.sidebar.button("Refresh Data"):
        st.rerun()
    
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)")
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

def simple_dashboard():
    """Simple text-based dashboard for when streamlit server isn't available"""
    dashboard = MetricsDashboard()
    
    print("\n" + "="*60)
    print("AI PLATFORM DASHBOARD - TEXT MODE")
    print("="*60)
    
    # Get metrics
    chat_df = dashboard.get_chat_metrics()
    rag_df = dashboard.get_rag_metrics()
    agent_df = dashboard.get_agent_metrics()
    
    # Overview
    print("\n📊 SYSTEM OVERVIEW")
    print("-" * 30)
    
    if not chat_df.empty:
        avg_latency = chat_df['latency_ms'].mean()
        total_cost = chat_df['cost'].sum()
        print(f"Average Chat Latency: {avg_latency:.0f}ms")
        print(f"Total Cost (24h): ${total_cost:.4f}")
    
    if not rag_df.empty:
        avg_retrieval = rag_df['retrieval_time_ms'].mean()
        avg_accuracy = rag_df['accuracy'].mean()
        print(f"Average Retrieval Time: {avg_retrieval:.0f}ms")
        print(f"Average Accuracy: {avg_accuracy:.1%}")
    
    if not agent_df.empty:
        success_rate = agent_df['success'].astype(bool).mean()
        avg_attempts = agent_df['attempts'].mean()
        print(f"Agent Success Rate: {success_rate:.1%}")
        print(f"Average Attempts: {avg_attempts:.1f}")
    
    # Recent activity
    print("\n📈 RECENT CHAT ACTIVITY")
    print("-" * 30)
    if not chat_df.empty:
        chat_df['datetime'] = pd.to_datetime(chat_df['timestamp'], unit='s')
        recent = chat_df.head(5)
        for _, row in recent.iterrows():
            print(f"{row['datetime'].strftime('%H:%M:%S')} | Tokens: {row['prompt_tokens']}→{row['completion_tokens']} | Latency: {row['latency_ms']}ms")
    
    print("\n🎯 AGENT PERFORMANCE")
    print("-" * 30)
    if not agent_df.empty:
        success_by_task = agent_df.groupby('task_type')['success'].mean()
        for task, rate in success_by_task.items():
            print(f"{task}: {rate:.1%} success rate")
    
    print("\n" + "="*60)
    print("For full interactive dashboard, run: streamlit run dashboard.py")
    print("="*60)

if __name__ == "__main__":
    main()