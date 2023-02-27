import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

const SearchRecipes = ({navigation, route}) => {
  return <Text> Search for recipes screen! {route.params.name}'s profile</Text>;
};

export default SearchRecipes;