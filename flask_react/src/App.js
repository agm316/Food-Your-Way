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

function goSearchRecipes()
{
}

function goAddRecipes()
{
}

// will connect this to our backend mongoDB database in order to get this working
function savedRecipes()
{
}

// this function will utilize an algorithm to suggest recipes to
// the user based on their previous search of recipes
function suggestRecipes()
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
  		onPress={Page}
  		title="Dashboard"
  		color="#50afff"
  		accessibilityLabel="Dashboard"/>
	</View>

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
  		onPress={savedRecipes}
  		title="Saved Recipes"
  		color="#50afff"
  		accessibilityLabel="Saved Recipes"/>
	</View>

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={suggestRecipes}
  		title="Suggested Recipes"
  		color="#50afff"
  		accessibilityLabel="Suggested recipes based on search"/>
	</View>

      </header>
    </div>
  );
}

export default App;
