import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

const SavedRecipes = ({navigation, route}) => {
  return <Text> Saved recipes screen! {route.params.name}'s profile</Text>;
};

export default SavedRecipes;