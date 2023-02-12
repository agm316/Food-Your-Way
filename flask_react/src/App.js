import logo from './logo.svg';
import './App.css';

import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

function goSearchRecipes()
{
}

function goAddRecipes()
{
}

function App() {
  return (
    <div className="App">
      <header className="App-header">

        <img src={logo} className="App-logo" alt="logo" />

        <p>
          Food Your Way
        </p>
	

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={goSearchRecipes}
  		title="Search Recipes"
  		color="#44a444"
  		accessibilityLabel="Search for recipes"/>
	</View> 

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={goAddRecipes}
  		title="Add Recipes"
  		color="#44a444"
  		accessibilityLabel="Add new recipes"/>
	</View>

      </header>
    </div>
  );
}

export default App;
