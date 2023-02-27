import logo from './logo.svg';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Dashboard from './Dashboard'
import Preferences from './Preferences'

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

function Page() {
  return (
    <div className="wrapper">
      <h1>Application</h1>
      <BrowserRouter>
        <Routes>
          <Route path="/dashboard">
            <Dashboard />
          </Route>
          <Route path="/preferences">
            <Preferences />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

function savedRecipes()
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
  		color="#50afff"
  		accessibilityLabel="Search for recipes"/>
	</View> 

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={goAddRecipes}
  		title="Add Recipes"
  		color="#50afff"
  		accessibilityLabel="Add new recipes"/>
	</View>

    <View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={Page}
  		title="Dashboard"
  		color="#50afff"
  		accessibilityLabel="Dashboard"/>
	</View>

    <View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={savedRecipes}
  		title="Saved Recipes"
  		color="#50afff"
  		accessibilityLabel="Saved Recipes"/>
	</View>

      </header>
    </div>
  );
}

export default App;
