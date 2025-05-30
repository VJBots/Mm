import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

class SMCAnalyzer:
    """
    Smart Money Concepts (SMC) and Inner Circle Trader (ICT) Logic Implementation
    """
    
    def __init__(self):
        self.swing_length = 5
        
    def identify_market_structure(self, df):
        """Identify Break of Structure (BOS) and Change of Character (CHoCH)"""
        try:
            swing_highs = self.find_swing_highs(df)
            swing_lows = self.find_swing_lows(df)
            
            structure = {
                'trend': 'NEUTRAL',
                'bos_detected': False,
                'choch_detected': False
            }
            
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                recent_highs = swing_highs[-2:]
                recent_lows = swing_lows[-2:]
                
                # Check for Higher Highs and Higher Lows (Bullish trend)
                if (recent_highs[1]['price'] > recent_highs[0]['price'] and 
                    recent_lows[1]['price'] > recent_lows[0]['price']):
                    structure['trend'] = 'BULLISH'
                    structure['bos_detected'] = True
                
                # Check for Lower Highs and Lower Lows (Bearish trend)
                elif (recent_highs[1]['price'] < recent_highs[0]['price'] and 
                      recent_lows[1]['price'] < recent_lows[0]['price']):
                    structure['trend'] = 'BEARISH'
                    structure['bos_detected'] = True
            
            return structure
            
        except Exception as e:
            logging.error(f"Error in market structure analysis: {e}")
            return {'trend': 'NEUTRAL', 'bos_detected': False, 'choch_detected': False}
    
    def find_swing_highs(self, df):
        """Find swing highs in the data"""
        swing_highs = []
        for i in range(self.swing_length, len(df) - self.swing_length):
            current_high = df['High'].iloc[i]
            is_swing_high = True
            
            for j in range(i - self.swing_length, i + self.swing_length + 1):
                if j != i and df['High'].iloc[j] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append({
                    'index': i,
                    'price': current_high,
                    'time': df.index[i]
                })
        
        return swing_highs
    
    def find_swing_lows(self, df):
        """Find swing lows in the data"""
        swing_lows = []
        for i in range(self.swing_length, len(df) - self.swing_length):
            current_low = df['Low'].iloc[i]
            is_swing_low = True
            
            for j in range(i - self.swing_length, i + self.swing_length + 1):
                if j != i and df['Low'].iloc[j] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append({
                    'index': i,
                    'price': current_low,
                    'time': df.index[i]
                })
        
        return swing_lows
    
    def get_smc_signal(self, df):
        """Generate SMC-based trading signal"""
        try:
            market_structure = self.identify_market_structure(df)
            
            if not market_structure:
                return None
            
            buy_score = 0
            sell_score = 0
            
            # Market structure bias
            if market_structure['trend'] == 'BULLISH':
                buy_score += 3
            elif market_structure['trend'] == 'BEARISH':
                sell_score += 3
            
            # BOS signals
            if market_structure['bos_detected']:
                if market_structure['trend'] == 'BULLISH':
                    buy_score += 4
                else:
                    sell_score += 4
            
            # Determine signal
            total_score = buy_score + sell_score
            if total_score == 0:
                return None
            
            if buy_score > sell_score and buy_score >= 3:
                confidence = min((buy_score / total_score) * 100, 95)
                return {
                    'signal_type': 'BUY',
                    'confidence': round(confidence, 1)
                }
            elif sell_score > buy_score and sell_score >= 3:
                confidence = min((sell_score / total_score) * 100, 95)
                return {
                    'signal_type': 'SELL',
                    'confidence': round(confidence, 1)
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Error generating SMC signal: {e}")
            return None
