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
          Food Your Way (Edit <code>src/App.js</code> and save to reload.) 
        </p>
	
	<Button
  	onPress={goSearchRecipes}
  	title="Search Recipes"
  	color="#841584"
  	accessibilityLabel="Search for recipes"/>

         <p>

        </p>

	<Button
  	onPress={goAddRecipes}
  	title="Add Recipes"
  	color="#841584"
  	accessibilityLabel="Add new recipes"/>

      </header>
    </div>
  );
}

export default App;
