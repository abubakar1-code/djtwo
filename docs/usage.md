# Usage

## Roles

### External

#### Company

Company that Supervisors and Employees belong to.

#### Supervisor

Supervisor for all Employees. Can request and see requests for all Employees of a company. Additionally able to batch upload and download requests. Has access to reporting metrics.

#### Employee

Can submit and view their own requests.

### Internal

#### Manager

Assigns Reviewer and Analyst for any incoming request and does final QC of report before returning request to client.

#### Reviewer

Does initial QC of Analyst reports.

#### Analyst

Writes report for the entity named in the request.


## Types of requests

### Corporate

Investigation of a corporate entity.

### Individual

Investigation of an individual.

### Custom

Custom investigation.

#### Fields

Required is required.

No check is available but not required.

Archived is keep but don't show.

## Statuses of Requests

### New

Initial report status after being request is created by Employee or Supervisor. Shows up in Manager queue.

### Assigned

In queue of Analyst but not yet started.

### In-Progress

Currently being worked on by Analyst.

### New Returned

Reviewer returns request to Analyst for rework.

### Review

After Analyst submission of request, goes to Reviewer queue.

### Completed

Reviewer submits to Manager.

### Submitted

Manager returns completed request to Client.

### Rejected

Analyst rejects request and request goes to Manager. Usually due to insufficient information.

### Incomplete

Manager marks rejected request as incomplete to return to Employee for more information.

### Deleted

Supervisor deletes an Incomplete request. Cannot delete an in progress request.

## Workflow

### Adding a New Client
1. Add company
1. Add employee to company

### Requests

1. Employee creates request. (New)
1. Manager assigns request to Analyst and Reviewer. (Assigned)
1. Analyst starts request. (In-Progress)
1. Analyst submits to Reviewer. (Review)
1. Back and forth between Analyst and Reviewer. (New Returned)
1. Reviewer submits to Manager. (Completed)
1. Manager final QC.
1. Manager returns to Employee. (Submitted)

## Reporting

Clock starts when Analyst starts request. Clock stops when Reviewer sends request to Manger.
