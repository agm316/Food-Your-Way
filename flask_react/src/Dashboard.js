import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

const Dashboard = ({navigation, route}) => {
  return <Text> Dashboard screen! {route.params.name}'s profile</Text>;
};

export default Dashboard;
