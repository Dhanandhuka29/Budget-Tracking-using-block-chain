pragma solidity >= 0.8.11 <= 0.8.11;

contract BudgetContract {
    string public users;
    string public budget;
    
    //function to save budget details to Blockchain
    function addBudgetDetails(string memory b) public {
        budget = b;	
    }
    //call to get budget details	
    function getBudgetDetails() public view returns (string memory) {
        return budget;
    }

    //function to save user details in Blockchain
    function addUsers(string memory u) public {
        users = u;	
    }
    //call to get user details	
    function getUsers() public view returns (string memory) {
        return users;
    }
    
    constructor() public {
        users = "";
	budget = "";
    }
}